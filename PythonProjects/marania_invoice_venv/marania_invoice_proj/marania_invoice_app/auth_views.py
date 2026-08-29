"""Views for the Login & User Management Module."""

import json
from datetime import datetime

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from .models import (
    ApplicationModule,
    AuditLog,
    CompanySettings,
    UserCategory,
    UserProfile,
)
from .modules import MODULE_REGISTRY

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _log(actor, action, entity_type=None, entity_id=None, entity_label=None,
         description="", detail="", auto_create_from_user=True):
    """Create an audit log entry. If actor is None but the request user is
    known it can be passed separately - keep signature simple: actor is a User.
    """
    AuditLog.objects.create(
        performed_by=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_label=entity_label,
        description=description,
        detail=detail,
    )


def _admin_required(user):
    """Return True if the user may access the Administration / User Management areas."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    profile = getattr(user, "user_profile", None)
    if profile is None:
        return False
    return "user_management" in profile.permitted_module_keys()


def _require_admin(view_func):
    """Decorator restricting a view to administrators."""
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not _admin_required(request.user):
            return HttpResponseForbidden(
                "You do not have permission to access this area."
            )
        return view_func(request, *args, **kwargs)
    return _wrapped


def _get_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


# ---------------------------------------------------------------------------
# Login / logout
# ---------------------------------------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse("dashboard"))

    company, _ = CompanySettings.objects.get_or_create(id=1)
    error = None

    # List of usernames locked out temporarily by failed attempts.
    failed = request.session.get("failed_attempts", {})
    locked_user = request.session.get("locked_username")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        if not username or not password:
            error = "Please enter both username and password."
        else:
            # Check the account first so we can give a clear message for
            # inactive/locked accounts before attempting authentication.
            account = User.objects.filter(username__iexact=username).first()

            if account is not None and not account.is_active:
                error = "Your account is inactive. Please contact your administrator."
                _log(account, "LOGIN_FAIL", "User", account.username, account.username,
                     "Login blocked: account inactive.")
            else:
                user = authenticate(request, username=username, password=password)

                if user is None:
                    # Record failed attempt (per-username throttle).
                    attempts = int(failed.get(username, 0)) + 1
                    failed[username] = attempts
                    request.session["failed_attempts"] = failed
                    if attempts >= 5:
                        request.session["locked_username"] = username
                    error = (
                        "Invalid username or password. "
                        + (f"Please try again later ({username} temporarily locked)."
                           if attempts >= 5 else f"Attempt {attempts} of 5.")
                    )
                    _log(None, "LOGIN_FAIL", "User", username, username,
                         f"Failed login attempt for username '{username}'.")
                else:
                    # Successful login.
                    login(request, user)
                    failed.pop(username, None)
                    request.session["failed_attempts"] = failed
                    request.session.pop("locked_username", None)
                    _log(user, "LOGIN", "User", user.username, user.username,
                         f"Successful login for '{user.username}'.")
                    return redirect(reverse("dashboard"))

    return render(request, "marania_invoice_app/login.html", {
        "company": company,
        "error": error,
        "locked_username": locked_user,
    })


def logout_view(request):
    if request.user.is_authenticated:
        _log(request.user, "LOGOUT", "User", request.user.username,
             request.user.username, f"Logout for '{request.user.username}'.")
    logout(request)
    return redirect(reverse("login"))


# ---------------------------------------------------------------------------
# Password change (self-service)
# ---------------------------------------------------------------------------

@login_required
def change_password_view(request):
    if request.method == "POST":
        current = request.POST.get("current_password") or ""
        new1 = request.POST.get("new_password1") or ""
        new2 = request.POST.get("new_password2") or ""

        if not request.user.check_password(current):
            return render(request, "marania_invoice_app/change_password.html",
                          {"error": "Your current password is incorrect."})
        if new1 != new2:
            return render(request, "marania_invoice_app/change_password.html",
                          {"error": "The new passwords do not match."})
        try:
            validate_password(new1, user=request.user)
        except ValidationError as e:
            return render(request, "marania_invoice_app/change_password.html",
                          {"error": "; ".join(e.messages)})

        request.user.set_password(new1)
        request.user.save(update_fields=["password"])
        update_session_auth_hash(request, request.user)
        profile = _get_profile(request.user)
        profile.last_password_change = timezone.now()
        profile.save(update_fields=["last_password_change"])
        _log(request.user, "PASSWORD_CHANGE", "User", request.user.username,
             request.user.username, "User changed their own password.")
        return render(request, "marania_invoice_app/change_password.html",
                      {"success": "Your password has been updated successfully."})

    return render(request, "marania_invoice_app/change_password.html") 


# ---------------------------------------------------------------------------
# User Management
# ---------------------------------------------------------------------------

@_require_admin
def admin_users(request):
    qs = User.objects.select_related("user_profile").all().order_by("username")

    search = request.GET.get("search", "").strip()
    category_id = request.GET.get("category", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        qs = qs.filter(
            Q(username__icontains=search)
            | Q(user_profile__full_name__icontains=search)
            | Q(user_profile__email__icontains=search)
        )
    if status == "Active":
        qs = qs.filter(is_active=True)
    elif status == "Inactive":
        qs = qs.filter(is_active=False)

    # Category filtering requires iterating since category is on profile.
    if category_id:
        try:
            qs = qs.filter(user_profile__category_id=int(category_id))
        except (ValueError, TypeError):
            pass

    sort = request.GET.get("sort", "username")
    allowed_sort = {"username", "is_active", "date_joined", "last_login"}
    if sort in allowed_sort:
        direction = request.GET.get("direction", "asc")
        field = sort if direction == "asc" else f"-{sort}"
        qs = qs.order_by(field)

    categories = UserCategory.objects.filter(is_active=True).order_by("name")

    return render(request, "marania_invoice_app/admin_users.html", {
        "users": qs,
        "categories": categories,
        "search": search,
        "selected_category": category_id,
        "selected_status": status,
    })


@_require_admin
def admin_user_edit(request, user_id=None):
    instance = None
    if user_id:
        instance = get_object_or_404(User, pk=user_id)

    is_self = instance is not None and instance.pk == request.user.pk

    all_modules = ApplicationModule.objects.filter(is_active=True).order_by("sort_order", "label")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        full_name = (request.POST.get("full_name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        category_id = request.POST.get("category") or ""
        status = request.POST.get("status") or "Active"
        module_keys = request.POST.getlist("modules")
        # Current/trusted category modules are prepopulated in the UI; only
        # explicit per-user overrides are stored here.
        explicit_module_keys = request.POST.getlist("explicit_modules")
        set_password_val = (request.POST.get("set_password") or "").strip()
        set_password2 = (request.POST.get("set_password2") or "").strip()

        errors = []

        if not username:
            errors.append("Username is required.")

        # Validate uniqueness (server-side).
        dup = User.objects.filter(username__iexact=username)
        if instance:
            dup = dup.exclude(pk=instance.pk)
        if dup.exists():
            errors.append("That username is already in use. Usernames must be unique.")

        if set_password_val or not instance:
            if not set_password_val:
                errors.append("A password is required for a new user.")
            elif set_password_val != set_password2:
                errors.append("Password and confirm password do not match.")
            else:
                try:
                    validate_password(set_password_val, user=instance)
                except ValidationError as e:
                    errors.append("; ".join(e.messages))

        if errors:
            return render(request, "marania_invoice_app/admin_user_form.html", {
                "user_obj": instance,
                "is_self": is_self,
                "all_modules": all_modules,
                "categories": UserCategory.objects.filter(is_active=True).order_by("name"),
                "users": User.objects.all(),
                "error": " ".join(errors),
                "form_values": request.POST,
            })

        category_obj = None
        if category_id:
            category_obj = UserCategory.objects.filter(pk=int(category_id)).first()

        if instance is None:
            instance = User.objects.create_user(
                username=username,
                password=set_password_val or "changeme",
                email=email,
            )
            action = "CREATE"
            entity_label = username
        else:
            instance.username = username
            instance.email = email
            if set_password_val:
                instance.set_password(set_password_val)
            action = "UPDATE"
            entity_label = instance.username

        is_active = (status == "Active")
        # Prevent an admin from deactivating their own account / removing own perms.
        if is_self:
            is_active = True

        # Never let a non-superuser self-demote off user management by removing
        # the explicit module; guard against locking themselves out.
        if is_self and action == "UPDATE":
            # Keep existing explicit modules but merge with submitted ones.
            profile = _get_profile(instance)
            profile.modules.add(*[m for m in profile.modules.all()])
            module_keys = [m.key for m in profile.modules.all()] + module_keys

        instance.is_active = is_active
        instance.save()

        profile = _get_profile(instance)
        profile.full_name = full_name
        profile.email = email
        profile.phone = phone
        profile.category = category_obj
        profile.status = "Active" if is_active else "Inactive"
        if action == "CREATE" or set_password_val:
            profile.last_password_change = timezone.now()

        # Apply module permissions: user picks explicit modules in the UI.
        chosen = set(ApplicationModule.objects.filter(key__in=module_keys))
        profile.modules.set(chosen)
        profile.save()

        detail = {
            "username": username,
            "category": category_obj.name if category_obj else "",
            "modules": sorted(m.key for m in chosen),
            "status": profile.status,
        }
        _log(request.user, "PASSWORD_RESET" if action=="UPDATE" and set_password_val else action,
             "User", str(instance.pk), entity_label,
             f"{action} user '{entity_label}'.", json.dumps(detail))

        return redirect(reverse("admin_users"))

    # GET - populate for editing.
    profile = _get_profile(instance) if instance else None
    pre_selected = set(profile.modules.values_list("key", flat=True)) if profile else set()

    return render(request, "marania_invoice_app/admin_user_form.html", {
        "user_obj": instance,
        "is_self": is_self,
        "all_modules": all_modules,
        "categories": UserCategory.objects.filter(is_active=True).order_by("name"),
        "pre_selected": pre_selected,
        "users": User.objects.all(),
    })


@_require_admin
@require_POST
def admin_user_toggle(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if target.pk == request.user.pk and not request.user.is_superuser:
        return HttpResponseForbidden("You cannot deactivate your own account.")

    target.is_active = not target.is_active
    target.save(update_fields=["is_active"])
    profile = _get_profile(target)
    profile.status = "Active" if target.is_active else "Inactive"
    profile.save(update_fields=["status"])
    action = "ACTIVATE" if target.is_active else "DEACTIVATE"
    _log(request.user, action, "User", str(target.pk), target.username,
         f"{action} user '{target.username}'.")
    return redirect(reverse("admin_users"))


@_require_admin
@require_POST
def admin_user_reset_password(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    new_password = (request.POST.get("new_password") or "").strip()
    if not new_password:
        return HttpResponseBadRequest("Password is required.")
    target.set_password(new_password)
    target.save(update_fields=["password"])
    profile = _get_profile(target)
    profile.last_password_change = timezone.now()
    profile.save(update_fields=["last_password_change"])
    _log(request.user, "PASSWORD_RESET", "User", str(target.pk), target.username,
         f"Administrator reset password for user '{target.username}'.")
    return redirect(reverse("admin_users"))


# ---------------------------------------------------------------------------
# User Categories / Roles
# ---------------------------------------------------------------------------

@_require_admin
def admin_categories(request):
    categories = UserCategory.objects.prefetch_related("modules").all().order_by("name")
    return render(request, "marania_invoice_app/admin_categories.html", {"categories": categories})


@_require_admin
def admin_category_edit(request, category_id=None):
    instance = None
    if category_id:
        instance = get_object_or_404(UserCategory, pk=category_id)

    all_modules = ApplicationModule.objects.filter(is_active=True).order_by("sort_order", "label")

    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        description = (request.POST.get("description") or "").strip()
        is_all_modules = request.POST.get("is_all_modules") == "on"
        is_active = request.POST.get("is_active") == "on"
        module_keys = request.POST.getlist("modules")
        original_name = instance.name if instance else None

        errors = []
        if not name:
            errors.append("Category name is required.")
        dup = UserCategory.objects.filter(name__iexact=name)
        if instance:
            dup = dup.exclude(pk=instance.pk)
        if dup.exists():
            errors.append("That category name already exists.")

        if errors:
            return render(request, "marania_invoice_app/admin_category_form.html", {
                "category": instance,
                "all_modules": all_modules,
                "error": " ".join(errors),
            })

        if instance is None:
            instance = UserCategory(name=name)
            is_new = True
        else:
            is_new = False
        instance.description = description
        instance.is_all_modules = is_all_modules
        instance.is_active = is_active
        instance.save()
        chosen = set(ApplicationModule.objects.filter(key__in=module_keys))
        instance.modules.set(chosen)

        _log(request.user, "CREATE" if is_new else "UPDATE", "UserCategory",
             str(instance.pk), instance.name,
             f"{'Created' if is_new else 'Updated'} category '{instance.name}'.",
             json.dumps({"name": name, "modules": sorted(m.key for m in chosen),
                        "all_modules": is_all_modules, "active": is_active}))
        return redirect(reverse("admin_categories"))

    pre_selected = set(instance.modules.values_list("key", flat=True)) if instance else set()
    return render(request, "marania_invoice_app/admin_category_form.html", {
        "category": instance,
        "all_modules": all_modules,
        "pre_selected": pre_selected,
    })


@_require_admin
@require_POST
def admin_category_toggle(request, category_id):
    category = get_object_or_404(UserCategory, pk=category_id)
    category.is_active = not category.is_active
    category.save(update_fields=["is_active"])
    action = "ACTIVATE" if category.is_active else "DEACTIVATE"
    _log(request.user, action, "UserCategory", str(category.pk), category.name,
         f"{action} category '{category.name}'.")
    return redirect(reverse("admin_categories"))


# ---------------------------------------------------------------------------
# Module registry management
# ---------------------------------------------------------------------------

@_require_admin
def admin_modules(request):
    modules = ApplicationModule.objects.all().order_by("sort_order", "label")
    if request.method == "POST":
        action = request.POST.get("action")
        module_id = request.POST.get("module_id")
        module = get_object_or_404(ApplicationModule, pk=module_id) if module_id else None

        if action == "toggle" and module:
            module.is_active = not module.is_active
            module.save(update_fields=["is_active"])
            _log(request.user, "PERMISSION", "ApplicationModule", str(module.pk),
                 module.label, f"{'Activated' if module.is_active else 'Deactivated'} module '{module.label}'.")
            return redirect(reverse("admin_modules"))

        if action == "save":
            key = (request.POST.get("key") or "").strip()
            label = (request.POST.get("label") or "").strip()
            prefix = (request.POST.get("url_prefix") or "").strip()
            icon = (request.POST.get("icon_name") or "").strip()
            sort_order = request.POST.get("sort_order") or 0
            is_active = request.POST.get("is_active") == "on"

            if module is None:
                module = ApplicationModule(key=key, label=label)
                is_new = True
            else:
                is_new = False

            module.label = label
            if key:
                module.key = key
            module.url_prefix = prefix or None
            module.icon_name = icon or None
            module.sort_order = int(sort_order) if str(sort_order).isdigit() else 0
            module.is_active = is_active
            module.save()

            _log(request.user, "CREATE" if is_new else "UPDATE", "ApplicationModule",
                 str(module.pk), module.label,
                 f"{'Created' if is_new else 'Updated'} module '{module.label}'.")
            return redirect(reverse("admin_modules"))

    return render(request, "marania_invoice_app/admin_modules.html", {"modules": modules})


# ---------------------------------------------------------------------------
# Audit trail
# ---------------------------------------------------------------------------

@_require_admin
def admin_audit(request):
    logs = AuditLog.objects.select_related("performed_by").all()

    action = request.GET.get("action", "").strip()
    search = request.GET.get("search", "").strip()
    if action:
        logs = logs.filter(action=action)
    if search:
        logs = logs.filter(
            Q(entity_label__icontains=search)
            | Q(description__icontains=search)
            | Q(performed_by__username__icontains=search)
        )

    logs = logs[:500]
    actions = AuditLog.ACTION_CHOICES
    return render(request, "marania_invoice_app/admin_audit.html", {
        "logs": logs,
        "actions": actions,
        "selected_action": action,
        "search": search,
    })
