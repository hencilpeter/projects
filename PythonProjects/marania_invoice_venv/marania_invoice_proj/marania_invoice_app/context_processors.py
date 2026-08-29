"""Context processors providing global branding/config and permission data.

These make ``config``, ``app_settings`` and the current user's permitted modules
available to every template, and store the user's permitted module keys in the
session so the permission middleware can enforce access server-side.
"""

from .models import CompanySettings


def _is_administrator(user):
    return bool(
        user.is_authenticated
        and (user.is_superuser or user.is_staff)
    )


def _is_user_manager(user):
    """A user who may manage other users (superuser/staff or user_management module)."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    profile = getattr(user, "user_profile", None)
    if profile is None:
        return False
    return "user_management" in profile.permitted_module_keys()


def _permitted_module_keys(user):
    """Return the set of module keys the user may access."""
    if not user.is_authenticated:
        return set()
    if user.is_superuser:
        # Superusers can access everything.
        from .modules import MODULE
        return set(MODULE.values())
    if user.is_staff:
        # Staff can access everything (via Django admin).
        from .modules import MODULE
        return set(MODULE.values())
    profile = getattr(user, "user_profile", None)
    if profile is None:
        return set()
    return profile.permitted_module_keys()


def base_context(request):
    from django.conf import settings

    company, _ = CompanySettings.objects.get_or_create(id=1)
    user = request.user

    permitted_keys = _permitted_module_keys(user)
    # Persist to session for the permission middleware.
    if user.is_authenticated:
        try:
            request.session["permitted_module_keys"] = sorted(permitted_keys)
        except Exception:
            pass

    is_superuser = user.is_authenticated and user.is_superuser
    is_user_manager = _is_user_manager(user)

    return {
        "config": company,  # exposes company_title, logo, etc.
        "app_settings": company,
        "company": company,
        "is_superuser": is_superuser,
        "is_user_manager": is_user_manager,
        "permitted_module_keys": permitted_keys,
        "DEFAULT_LOGO_URL": "/static/images/marania_eagle_logo.png",
    }
