{
    "name": "Import Sale Lines",
    "summary": """
       Import Sale Lines
    """,
    "description": """
       Import Sale Lines
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Purchase",
    "version": "15.0.1.0.1",
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "depends": ["sale", "report_xlsx"],
    "data": [
        "report/report_action.xml",
        "wizard/import_wizard.xml",
    ],
}
