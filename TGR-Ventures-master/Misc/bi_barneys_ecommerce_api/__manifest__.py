{
    "name": "Odoo API for Barneys E-commerce",
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "category": "API",
    "summary": "Odoo API for Barneys E-commerce Websites",
    "description": """
This module will provide an API for e-commerce platforms to create and validate sale orders through ODOO
""",
    "version": "15.0.1.0.0",
    "depends": [
        "base",
        "sale",
        "sale_management",
        "delivery",
        "odoo_auth2",
        "stock",
        "common_connector_library",
        "odoo_magento2_ept",
        "bi_customer_generic_customization",
        "odoo_ecommerce_api",
        "bi_barneys_master",
        "bi_dropshipping_discount",
    ],
    "data": [
        "data/data.xml",
        "views/res_config_settings_views.xml",
        "views/payment_method_code.xml",
        "views/sale_order_views.xml",
        "views/ecommerce_api_log_views.xml",
        "views/customer_class_views.xml",
        "views/delivery_carrier.xml",
        "views/stock_picking.xml",
    ],
    "external_dependencies": {"python": ["oauthlib"]},
    "application": False,
    "auto_install": False,
    "installable": True,
    "license": "LGPL-3",
}

# Please update PyopenSSL to v22.1.0.0 before installing oauthlib library. Otherwise, python env will be crashed
