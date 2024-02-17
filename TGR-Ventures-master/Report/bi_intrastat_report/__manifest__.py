{
    "name": "Intrastat Report",
    "summary": """
     Intrastat Report
    """,
    "description": """
       Intrastat Report
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Account",
    "version": "15.0.1.0.1",
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "depends": ["account", "account_intrastat", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "report/intrastat_report_action.xml",
        "views/account_account_tag.xml",
        "views/account_tax.xml",
        "wizard/intrastat_report_wizard.xml",
    ],
}
