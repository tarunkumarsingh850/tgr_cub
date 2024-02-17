{
    "name": "Drop Shipping Discount",
    "summary": """
        Module is used for Discount for Drop Shipping Customers""",
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Sale",
    "version": "15.0.1",
    "depends": ["base", "sale", "product", "account", "odoo_ecommerce_api", "bi_inventory_generic_customisation"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/sale_order.xml",
    ],
    "assets": {
        "web.assets_qweb": [
            "bi_dropshipping_discount/static/src/xml/tax_totals.xml",
        ],
    },
}
