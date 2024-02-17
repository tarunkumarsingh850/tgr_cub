{
    "name": "Import Account statement Bank Lines",
    "summary": """
        Module is used to Import account bank statement lines
    """,
    "description": """
            Module is used to Import Account statement Lines
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
        "views/account_bank_statement_line.xml",
        "wizard/bank_statement_wizard.xml",
        "report/report_action.xml",
    ],
}
