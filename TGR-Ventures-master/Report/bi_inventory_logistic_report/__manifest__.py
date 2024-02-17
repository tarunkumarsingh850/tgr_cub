{
    "name": "BI Inventory Logistic Report",
    "summary": """
        Inventory Logistics Report""",
    "description": """
        This module print customise Inventory logistic excel report.
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Stock",
    "version": "15.0.0.1",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/inventory_logistic_wizard_view.xml",
        "report/inventory_logistic_report_action.xml",
    ],
}
