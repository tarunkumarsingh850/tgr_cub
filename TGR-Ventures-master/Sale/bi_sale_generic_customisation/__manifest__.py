{
    "name": "Sale Customization",
    "summary": """
        Sale Customization""",
    "description": """
        Sale Customization
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Uncategorized",
    "version": "15.0.1",
    "depends": [
        "base",
        "sale",
        "bi_sale_type",
        "partner_manual_rank",
        "bi_hold_reason",
        "stock",
        "odoo_magento2_ept",
        "bi_inventory_generic_customisation",
        "sale_margin",
    ],
    "data": [
        "data/server_actions.xml",
        "security/ir.model.access.csv",
        "views/sale_order.xml",
        "wizards/sale_warehouse_update.xml",
        "wizards/order_unhold_reason_wizard.xml",
        "views/res_config.xml",
    ],
}
