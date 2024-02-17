{
    "name": "Product Report Export",
    "summary": """
     Product Report Export
    """,
    "description": """
       Product Report Export
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Purchase",
    "version": "15.0.1.0.1",
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "depends": ["stock", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "report/report_action.xml",
        "wizard/wizard.xml",
    ],
}
