{
    "name": "Picking Report",
    "summary": """
     Picking Report
    """,
    "description": """
       Picking Report
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Stock",
    "version": "15.0.1.0.1",
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "depends": ["stock", "stock_picking_batch", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "report/stock_picking.xml",
        "wizard/picking_report_wizard.xml",
    ],
}
