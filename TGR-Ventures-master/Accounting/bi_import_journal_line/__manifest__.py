{
    "name": "Import Journal lines",
    "summary": """
       Module is used to update the Journal lines import.
    """,
    "description": """
       Module is used to update the Journal lines import
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Account",
    "version": "15.0.1.0.1",
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "depends": ["account", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "views/journal_entry.xml",
        "wizard/journal_line_wizard.xml",
        "report/report_action.xml",
    ],
}
