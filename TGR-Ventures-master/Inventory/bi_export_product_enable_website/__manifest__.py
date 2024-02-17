{
    "name": "Export products Website",
    "summary": """
        Export products Website""",
    "description": """
        IExport products Website
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Inventory",
    "version": "0.1",
    "depends": ["base", "stock", "odoo_magento2_ept", "bi_inventory_generic_customisation"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/cron.xml",
        "view/pack_size_configurable.xml",
        "view/magento_product_configurable.xml",
        "wizard/export_product_website.xml",
        "wizard/update_product_enable_disable.xml",
        "report/report_action.xml",
    ],
}
