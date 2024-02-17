{
    "name": "BI Batch Transfer ZPL Barcode Label",
    "summary": """
        Print batch transfer ZPL barcode label""",
    "description": """
        To take batch transfer ZPL barcode label from Odoo""",
    "author": "Bassam Infotech",
    "website": "http://www.bassaminfotech.in",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Uncategorized",
    "version": "15.0.0.1",
    "depends": ["base", "stock_picking_batch"],
    "data": [
        "views/stock_picking_batch_view.xml",
        "report/barcode_report_action.xml",
        "report/barcode_report_template.xml",
    ],
}
