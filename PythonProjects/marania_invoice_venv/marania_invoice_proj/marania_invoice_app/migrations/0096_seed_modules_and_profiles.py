from django.db import migrations
from django.apps import apps as django_apps


def seed_modules(apps, schema_editor):
    Module = apps.get_model("marania_invoice_app", "ApplicationModule")
    registry = [
        {"key": "dashboard", "label": "Dashboard", "icon_name": "home", "url_prefix": "/", "sort_order": 1},
        {"key": "masters", "label": "Masters", "icon_name": "layers", "url_prefix": "/parties", "sort_order": 2},
        {"key": "transactions", "label": "Transactions", "icon_name": "shopping-cart", "url_prefix": "/orders", "sort_order": 3},
        {"key": "accounting", "label": "Accounting", "icon_name": "file", "url_prefix": "/invoice_entry", "sort_order": 4},
        {"key": "reports_tools", "label": "Reports & Tools", "icon_name": "pie-chart", "url_prefix": "/reports", "sort_order": 5},
        {"key": "configuration", "label": "Configuration", "icon_name": "sliders", "url_prefix": "/configuration", "sort_order": 6},
        {"key": "analytics", "label": "Analytics", "icon_name": "activity", "url_prefix": "/production", "sort_order": 7},
        {"key": "administration", "label": "Administration", "icon_name": "settings", "url_prefix": "/settings/company", "sort_order": 8},
        {"key": "user_management", "label": "User Management", "icon_name": "users", "url_prefix": "/admin/users", "sort_order": 9},
    ]
    for entry in registry:
        Module.objects.update_or_create(key=entry["key"], defaults=entry)


def create_profiles_for_existing_users(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Profile = apps.get_model("marania_invoice_app", "UserProfile")
    for user in User.objects.all():
        Profile.objects.update_or_create(
            user=user,
            defaults={"email": user.email or "", "status": "Active" if user.is_active else "Inactive"},
        )


def reverse_func(apps, schema_editor):
    # Non-destructive by design; leave seeded data in place.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("marania_invoice_app", "0095_applicationmodule_usercategory_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_modules, reverse_func),
        migrations.RunPython(create_profiles_for_existing_users, reverse_func),
    ]
