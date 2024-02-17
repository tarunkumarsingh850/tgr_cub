{
    "name": "Res Partner Generic Customisation",
    "summary": """
        Res Partner Generic Customisation""",
    "description": """
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Res Partner",
    "version": "15.0.0.1",
    "depends": ["purchase", "account", "partner_manual_rank", "base", "delivery", "bi_inventory_generic_customisation"],
    "data": [
        "security/ir.model.access.csv",
        "views/vendor_class_view.xml",
        "views/product_type_view.xml",
        "views/partner_view_inherit.xml",
        "views/po_inherit.xml",
        "views/partner_bank.xml",
        "views/res_company.xml",
    ],
}
