{
    "name": "bi_sale_configuration",
    "description": """
        adding field to sale order settings
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Sale",
    "version": "15.0.0.1",
    "depends": ["sale", "bi_sale_generic_customisation"],
    "data": [
        "security/ir.model.access.csv",
        "views/logistics_master.xml",
        "views/res_company.xml",
        "views/sale_order_inherit.xml",
    ],
}
