{
    "name": "Odoo API for E-commerce",
    "author": "Bassam Infotec LLP",
    "website": "",
    "support": "",
    "category": "API",
    "summary": "Odoo API for E-commerce Websites",
    "description": """
This module will provide an API for e-commerce platforms to create and validate sale orders through ODOO
""",
    "version": "15.0.1.0.5",
    "depends": ["base", "sale", "sale_management", "odoo_auth2", "stock", "delivery", "common_connector_library"],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
        "views/sale_order_views.xml",
        "views/ecommerce_api_log_views.xml",
        "views/sale_workflow_process_views.xml",
        "views/stock_warehouse_views.xml",
        "views/res_partner_views.xml",
        "views/stock_picking.xml",
        "views/delivery_carrier.xml",
    ],
    "external_dependencies": {"python": ["oauthlib"]},
    "application": False,
    "auto_install": False,
    "installable": True,
    "license": "LGPL-3",
}

# Please update PyopenSSL to v22.1.0.0 before installing oauthlib library. Otherwise, python env will be crashed
