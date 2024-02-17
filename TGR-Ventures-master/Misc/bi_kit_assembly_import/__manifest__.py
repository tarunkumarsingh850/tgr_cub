{
    "name": "Kit Assembly Import",
    "summary": """Import massive records of kit assembly/dissembly to odoo.""",
    "version": "15.0.1.0.0",
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "lisence": "LGPL-3",
    "depends": [
        "base",
        "bi_kit_assembly",
        "report_xlsx",
        "bi_barcode",
    ],
    "data": [
        "security/ir.model.access.csv",
        "reports/reports.xml",
        "wizards/kit_assembly_import.xml",
    ],
}
