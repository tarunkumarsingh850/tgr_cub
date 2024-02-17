{
    "name": "Kit Assembly",
    "summary": """
       Kit Assembly""",
    "description": """
        Kit Assembly
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "LGPL-3",
    "category": "Uncategorized",
    "version": "15.1",
    "depends": ["base", "stock", "product", "account"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/sequence.xml",
        "views/bom.xml",
        "views/product.xml",
        "views/kit_assembly.xml",
        "views/stock_move.xml",
        "views/account_journal.xml",
        "views/config.xml",
    ],
}
