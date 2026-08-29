from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import (
    ApplicationModule,
    AuditLog,
    CompanySettings,
    UserCategory,
    UserProfile,
)


class LoginModuleBase(TestCase):
    def setUp(self):
        self.client = Client()
        # Ensure the company settings singleton exists (with new fields).
        self.company, _ = CompanySettings.objects.get_or_create(id=1)
        # Seed modules if not present (they are normally seeded by migration,
        # but tests may run against an empty schema).
        ApplicationModule.objects.update_or_create(
            key="dashboard", defaults={"label": "Dashboard", "url_prefix": "/"}
        )
        ApplicationModule.objects.update_or_create(
            key="masters", defaults={"label": "Masters", "url_prefix": "/parties"}
        )
        ApplicationModule.objects.update_or_create(
            key="user_management",
            defaults={"label": "User Management", "url_prefix": "/admin/users"},
        )
        ApplicationModule.objects.update_or_create(
            key="administration",
            defaults={"label": "Administration", "url_prefix": "/settings/company"},
        )
        # Superuser for admin operations.
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@x.com", password="AdminPass123!"
        )
        self.admin.set_password("AdminPass123!")
        self.admin.save()
        # Profile for admin
        UserProfile.objects.update_or_create(user=self.admin, defaults={"status": "Active"})
        self.client.force_login(self.admin)


class LoginTests(LoginModuleBase):
    def test_login_page_loads(self):
        self.client.logout()
        resp = self.client.get(reverse("login"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Username")
        self.assertContains(resp, "Password")

    def test_valid_login_redirects_to_dashboard(self):
        self.client.logout()
        resp = self.client.post(reverse("login"), {
            "username": "admin", "password": "AdminPass123!",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("dashboard"), resp.url)

    def test_invalid_login_shows_error(self):
        self.client.logout()
        resp = self.client.post(reverse("login"), {
            "username": "admin", "password": "WrongPass!",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Invalid username or password")

    def test_inactive_user_cannot_login(self):
        self.client.logout()
        u = User.objects.create_user(
            username="disabled", password="Password123!",
        )
        u.is_active = False
        u.save()
        UserProfile.objects.update_or_create(user=u, defaults={"status": "Inactive"})
        resp = self.client.post(reverse("login"), {
            "username": "disabled", "password": "Password123!",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "inactive")


class UserManagementTests(LoginModuleBase):
    def test_create_user(self):
        resp = self.client.post(reverse("admin_user_new"), {
            "username": "newuser",
            "full_name": "New User",
            "email": "new@x.com",
            "set_password": "Passw0rd!",
            "set_password2": "Passw0rd!",
            "status": "Active",
            "modules": ["masters"],
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_duplicate_username_rejected(self):
        User.objects.create_user(username="dup", password="Passw0rd!")
        resp = self.client.post(reverse("admin_user_new"), {
            "username": "dup",
            "set_password": "Passw0rd!",
            "set_password2": "Passw0rd!",
            "status": "Active",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "already in use")

    def test_deactivate_user_prevents_login(self):
        u = User.objects.create_user(username="temp", password="Passw0rd!")
        UserProfile.objects.update_or_create(user=u, defaults={"status": "Active"})
        # Deactivate via admin.
        self.client.post(reverse("admin_user_toggle", args=[u.id]))
        u.refresh_from_db()
        self.assertFalse(u.is_active)
        self.client.logout()
        resp = self.client.post(reverse("login"), {
            "username": "temp", "password": "Passw0rd!",
        })
        self.assertContains(resp, "inactive")

    def test_password_reset_works(self):
        u = User.objects.create_user(username="resetme", password="OldPass123!")
        UserProfile.objects.update_or_create(user=u, defaults={"status": "Active"})
        self.client.post(reverse("admin_user_edit", args=[u.id]), {
            "username": "resetme",
            "set_password": "NewPass456!",
            "set_password2": "NewPass456!",
            "status": "Active",
            "modules": ["dashboard"],
        })
        u.refresh_from_db()
        self.assertTrue(u.check_password("NewPass456!"))
        self.assertTrue(
            AuditLog.objects.filter(action="PASSWORD_RESET", entity_id=str(u.id)).exists()
        )


class ModulePermissionTests(LoginModuleBase):
    def test_non_admin_cannot_access_user_management(self):
        self.client.logout()
        u = User.objects.create_user(username="worker", password="Passw0rd!")
        UserProfile.objects.update_or_create(user=u, defaults={"status": "Active"})
        # Worker gets a category granting only the "masters" module, NOT
        # user_management.
        masters = ApplicationModule.objects.get(key="masters")
        cat = UserCategory.objects.create(name="Worker", is_active=True)
        cat.modules.set([masters])
        u.user_profile.category = cat
        u.user_profile.save()
        self.client.force_login(u)
        # Worker lacks user_management, so admin URL should be denied.
        resp = self.client.get(reverse("admin_users"))
        self.assertEqual(resp.status_code, 403)

    def test_permitted_user_can_access_user_management(self):
        self.client.logout()
        u = User.objects.create_user(username="manager", password="Passw0rd!")
        UserProfile.objects.update_or_create(user=u, defaults={"status": "Active"})
        um = ApplicationModule.objects.get(key="user_management")
        u.user_profile.modules.add(um)
        self.client.force_login(u)
        self.client.session["permitted_module_keys"] = sorted(
            u.user_profile.permitted_module_keys()
        )
        self.client.session.save()
        resp = self.client.get(reverse("admin_users"))
        self.assertEqual(resp.status_code, 200)


class AuditTrailTests(LoginModuleBase):
    def test_login_logged(self):
        self.client.logout()
        self.client.post(reverse("login"), {
            "username": "admin", "password": "AdminPass123!",
        })
        self.assertTrue(
            AuditLog.objects.filter(action="LOGIN", entity_id="admin").exists()
        )

    def test_user_creation_logged(self):
        self.client.post(reverse("admin_user_new"), {
            "username": "audited_user",
            "set_password": "Passw0rd!",
            "set_password2": "Passw0rd!",
            "status": "Active",
            "modules": ["dashboard"],
        })
        self.assertTrue(
            AuditLog.objects.filter(
                action="CREATE", entity_type="User", entity_label="audited_user"
            ).exists()
        )
