{
    "name": "RoW Picking Report",
    "summary": """
     Picking Report for orders to rest of the world
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Stock",
    "version": "15.0.1.0",
    "depends": ["stock", "stock_picking_batch", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "report/report_action.xml",
        "wizard/row_picking_report_wizard.xml",
    ],
}
