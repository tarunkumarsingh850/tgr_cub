{
    "name": "TGR Dashboards",
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "category": "Dashboard",
    "summary": "Dashboards for TGR",
    "description": """
Dashboards for TGR
""",
    "version": "15.0.1.3.3",
    "depends": [
        "base",
        "web",
        "stock",
        "crm",
        "sale_management",
        "bi_inventory_generic_customisation",
        "bi_customer_generic_customization",
    ],
    "data": [
        "views/dashboard_views.xml",
        "views/product_breeder_views.xml",
        "views/res_partner_views.xml",
        "views/res_users_views.xml",
        "views/stock_warehouse_views.xml",
        'security/ir.model.access.csv'
    ],
    "assets": {
        "web.assets_backend": [
            # scss
            "tgr_dashboards/static/src/scss/dashboard.scss",
            # js
            "tgr_dashboards/static/src/js/tgr_sales_dashboard.js",
            "tgr_dashboards/static/src/js/tgr_crm_dashboard.js",
            "tgr_dashboards/static/src/js/tgr_purchase_dashboard.js",
        ],
        "web.assets_qweb": [
            "tgr_dashboards/static/src/xml/tgr_sales_dashboard.xml",
            "tgr_dashboards/static/src/xml/tgr_crm_dashboard.xml",
            "tgr_dashboards/static/src/xml/tgr_purchase_dashboard.xml",
        ],
    },
    "application": True,
    "auto_install": False,
    "installable": True,
    "license": "LGPL-3",
}
