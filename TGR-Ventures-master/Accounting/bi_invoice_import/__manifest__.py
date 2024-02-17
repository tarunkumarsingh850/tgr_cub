{
    "name": "Invoice Import",
    "summary": """Import invoice from excel""",
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Accounting",
    "version": "15.0.0.1",
    "depends": ["base", "account"],
    "data": ["security/ir.model.access.csv", "wizards/invoice_import.xml"],
    "external_dependencies": {
        "python": ["xlrd"],
    },
}
