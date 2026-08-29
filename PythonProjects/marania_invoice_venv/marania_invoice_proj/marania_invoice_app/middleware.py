"""Server-side module access enforcement middleware.

Prevents users from accessing URLs belonging to modules for which they have no
permission. This is independent of the UI: even if a user navigates directly to
a protected URL, the request is rejected unless the module is permitted.

Enforcement rules:
  * Anonymous users are redirected to the login page.
  * Authenticated superusers and staff may access everything.
  * Authenticated users may access a module only if its key is in their
    permitted set (login page and a few public paths are always allowed).
"""

from django.shortcuts import redirect
from django.urls import resolve

# Public paths that never require module permission. Note: all application
# URLs are mounted under '/invoice/', so both the bare and mounted forms are
# treated as public.
_PUBLIC_PREFIXES = (
    "/login",
    "/invoice/login",
    "/static/",
    "/uploads/",
    "/admin/",  # Django admin has its own auth
    "/favicon.ico",
)

# Url names that are always reachable regardless of auth/module permissions.
_PUBLIC_URL_NAMES = {
    "login",
    "change_password",
    "password_reset",
    "password_reset_done",
    "password_reset_confirm",
    "password_reset_complete",
}


class ModuleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    # enable below code to bypass the login
    # def __call__(self, request):
    #     # ---- AUTO-LOGIN: bypasses user-specific login (temporary dev override) ----
    #     from django.contrib.auth import get_user_model
    #     User = get_user_model()
    #     force_user = User.objects.filter(is_superuser=True).first()
    #     if force_user is not None:
    #         request.user = force_user
    #     # --------------------------------------------------------------------------
    #     return self.get_response(request)

    # And, disable below code to bypass the login
    def __call__(self, request):
        if not self._access_allowed(request):
            if request.user.is_authenticated:
                # Authenticated but not permitted -> 403 with a helpful page.
                return self._denied(request)
            # Anonymous -> send to login.
            return redirect("login")
        return self.get_response(request)

    def _access_allowed(self, request):
        from .modules import module_for_path

        # Always allow public / administrative / asset paths.
        path = request.path
        for prefix in _PUBLIC_PREFIXES:
            if path == prefix or path.startswith(prefix):
                return True

        # Allow explicitly-public URL names (e.g. the login page itself).
        try:
            match = resolve(request.path_info)
            if match.url_name in _PUBLIC_URL_NAMES:
                return True
        except Exception:
            pass

        user = request.user
        if not user.is_authenticated:
            return False

        # Superusers and staff have unrestricted access.
        if user.is_superuser or user.is_staff:
            return True

        # Determine which module this path belongs to (if any).
        module_key = module_for_path(path)
        if module_key is None:
            # Not a guarded path -> allow through (page-level checks still guard).
            return True

        # Compute permitted set directly from the user's profile (authoritative),
        # rather than relying on the session which may not be populated yet.
        permitted = set()
        profile = getattr(user, "user_profile", None)
        if profile is not None:
            permitted = profile.permitted_module_keys()
        if not permitted:
            permitted = set(request.session.get("permitted_module_keys") or [])

        # Ensure login page and dashboard base are reachable. Dashboard granted
        # to every authenticated user.
        if module_key == "dashboard":
            return True

        return module_key in permitted

    def _denied(self, request):
        from django.shortcuts import render

        return render(
            request,
            "marania_invoice_app/403.html",
            {"error_title": "Access Denied", "error_message": "You do not have permission to access this module."},
            status=403,
        )
