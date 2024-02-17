{
    "name": "BI Backorder Report",
    "summary": """
        Backorder Report""",
    "description": """
        This module print backorder products which are not available.
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
        "wizard/backorder_reserved_product_wizard.xml",
        "report/backorder_inventory_report_action.xml",
    ],
}
