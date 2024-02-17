{
    "name": "Import Invoice lines",
    "summary": """
       Module is used to update the Invoice lines import.
    """,
    "description": """
       Module is used to update the Invoice lines import
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
        "views/account_move.xml",
        "wizard/invoice_line_wizard.xml",
        "report/report_action.xml",
    ],
}
