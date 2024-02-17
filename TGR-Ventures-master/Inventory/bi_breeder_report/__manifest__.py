{
    "name": "Breeder Report",
    "summary": """
        Breeder Report""",
    "description": """
        Breeder Report
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Inventory",
    "version": "15.0.0.1",
    "depends": ["stock", "bi_inventory_generic_customisation", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "report/report_action.xml",
        "wizard/breeder_report_wizard.xml",
        "views/stock_views.xml",
    ],
}
