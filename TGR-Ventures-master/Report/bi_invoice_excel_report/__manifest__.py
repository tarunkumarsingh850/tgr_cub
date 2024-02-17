{
    "name": "Invoice Excel Printout",
    "summary": """
        Invoice Excel Printout""",
    "description": """
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Reporting",
    "version": "15.0.0.1",
    "depends": ["account", "report_xlsx", "sale"],
    "data": [
        "views/account_move.xml",
        "report/invoice_excel_report.xml",
        "views/account_move.xml",
        "report/invoice_memo_excel_report.xml",
    ],
}
