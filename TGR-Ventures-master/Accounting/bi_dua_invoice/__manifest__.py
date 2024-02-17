{
    "name": "Dua Invoice",
    "summary": """
        Import Invoice E invoicing""",
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Accounting",
    "version": "15.0.1",
    "depends": ["base", "account", "bi_accounting_generic_customization"],
    "data": [
        "data/sequence.xml",
        "security/ir.model.access.csv",
        "views/import_invoice_views.xml",
    ],
}
