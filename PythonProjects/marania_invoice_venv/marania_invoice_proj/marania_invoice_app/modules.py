"""Module registry and permission helpers for the Login & User Management Module.

This is the single source of truth for the application's module-level access
control. Each module maps a unique ``key`` and ``label`` to one or more URL
prefixes. The permission enforcement layers (context processor + middleware)
use this registry so that adding a new module is a small, non-invasive change.
"""

# Module keys (stable identifiers used in permissions)
MODULE = {
    "DASHBOARD": "dashboard",
    "MASTERS": "masters",
    "TRANSACTIONS": "transactions",
    "ACCOUNTING": "accounting",
    "REPORTS_TOOLS": "reports_tools",
    "CONFIGURATION": "configuration",
    "ANALYTICS": "analytics",
    "ADMINISTRATION": "administration",
    "USER_MANAGEMENT": "user_management",
}

# Default seed data describing the application's modules and their URL prefixes.
MODULE_REGISTRY = [
    {
        "key": MODULE["DASHBOARD"],
        "label": "Dashboard",
        "icon_name": "home",
        "url_prefixes": ["/"],
        "sort_order": 1,
        "is_active": True,
        "guard_all": True,  # everyone (who is logged in) gets dashboard
    },
    {
        "key": MODULE["MASTERS"],
        "label": "Masters",
        "icon_name": "layers",
        "url_prefixes": [
            "/parties",
            "/products",
            "/materials",
            "/price-list",
            "/customer-price-catalog",
            "/customer-price-dictionary",
        ],
        "sort_order": 2,
        "is_active": True,
    },
    {
        "key": MODULE["TRANSACTIONS"],
        "label": "Transactions",
        "icon_name": "shopping-cart",
        "url_prefixes": [
            "/orders",
            "/sales",
            "/purchases",
            "/twine-inventory",
        ],
        "sort_order": 3,
        "is_active": True,
    },
    {
        "key": MODULE["ACCOUNTING"],
        "label": "Accounting",
        "icon_name": "file",
        "url_prefixes": [
            "/invoice_entry",
            "/payment-receipts",
            "/payment-allocations",
            "/opening-balances",
            "/expenses",
            "/settlement-invoices",
        ],
        "sort_order": 4,
        "is_active": True,
    },
    {
        "key": MODULE["REPORTS_TOOLS"],
        "label": "Reports & Tools",
        "icon_name": "pie-chart",
        "url_prefixes": [
            "/reports",
            "/profit-loss",
            "/invoice-aging-report",
            "/outstanding-payment-list",
            "/view_gst_calculator",
        ],
        "sort_order": 5,
        "is_active": True,
    },
    {
        "key": MODULE["CONFIGURATION"],
        "label": "Configuration",
        "icon_name": "sliders",
        "url_prefixes": [
            "/configuration/material-conversion-ratio",
            "/configuration/processing-cost",
            "/configuration/machine-operational-cost",
            "/configuration/additional-cost",
            "/configuration/extra-mesh-config",
            "/configuration/price-list-colour-config",
        ],
        "sort_order": 6,
        "is_active": True,
    },
    {
        "key": MODULE["ANALYTICS"],
        "label": "Analytics",
        "icon_name": "activity",
        "url_prefixes": [
            "/season-trends",
            "/trend-analytics",
            "/production",
            "/analytics",
            "/piece-weight-analyser",
            "/price-list-generator",
        ],
        "sort_order": 7,
        "is_active": True,
    },
    {
        "key": MODULE["ADMINISTRATION"],
        "label": "Administration",
        "icon_name": "settings",
        "url_prefixes": [
            "/settings/company",
            "/export",
            "/import-all",
            "/export-all",
            "/clean-all",
            "/sync",
        ],
        "sort_order": 8,
        "is_active": True,
    },
    {
        "key": MODULE["USER_MANAGEMENT"],
        "label": "User Management",
        "icon_name": "users",
        "url_prefixes": [
            "/admin/users",
            "/admin/categories",
            "/admin/modules",
            "/admin/audit",
        ],
        "sort_order": 9,
        "is_active": True,
    },
]

# Consolidated mapping for fast lookups
URL_PREFIX_TO_MODULE = {}


def _build_lookup():
    URL_PREFIX_TO_MODULE.clear()
    registry = [m for m in MODULE_REGISTRY if m.get("is_active", True)]
    for m in registry:
        module_key = m["key"]
        for prefix in m.get("url_prefixes", []):
            # Longest prefixes win (e.g. '/configuration/processing-cost' vs '/')
            existing = URL_PREFIX_TO_MODULE.get(prefix)
            if existing is None or len(prefix) > len(existing):
                URL_PREFIX_TO_MODULE[prefix] = module_key
    return URL_PREFIX_TO_MODULE


_build_lookup()


# Mount prefix under which all application URLs are served (see project urls.py:
#   path('invoice/', include('marania_invoice_app.urls'))). The registry prefixes
# below are defined root-relative; this is stripped before matching.
APP_URL_PREFIX = "/invoice"


def module_for_path(path):
    """Return the module key governing the given URL path, or None if unguarded.

    Guards the dashboard and all registered module prefixes. Returns None for
    public/unlisted paths so they are not blocked by the middleware.
    """
    if not path:
        return None

    # Normalize: strip the application mount prefix so registry prefixes (which
    # are root-relative) match the actual request path.
    normalized = path
    if APP_URL_PREFIX and (path == APP_URL_PREFIX or path.startswith(APP_URL_PREFIX + "/")):
        normalized = path[len(APP_URL_PREFIX):] or "/"

    best_key = None
    best_len = -1
    for prefix, module_key in URL_PREFIX_TO_MODULE.items():
        if normalized == prefix or normalized.startswith(prefix):
            if len(prefix) > best_len:
                best_len = len(prefix)
                best_key = module_key
    return best_key
