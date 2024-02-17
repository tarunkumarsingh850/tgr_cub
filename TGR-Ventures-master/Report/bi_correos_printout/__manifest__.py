{
    "name": "Correos Manifest Report",
    "summary": """
        Module is used for Correos Manifest Report""",
    "author": "Bassam Infotech LLP",
    "license": "LGPL-3",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "category": "Stock",
    "version": "15.0.0.1",
    "depends": ["stock", "delivery"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/correos_wizard.xml",
        "report/report_header.xml",
        "report/paperformact.xml",
        "report/correos_printout.xml",
        "report/report_action.xml",
        "view/delivery_carrier.xml",
    ],
}
