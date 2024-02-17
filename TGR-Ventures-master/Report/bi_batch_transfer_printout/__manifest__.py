{
    "name": "Bi Batch Transfer Print",
    "summary": """
        To batch transfer prints from Odoo""",
    "description": """
        To take batch transfer prints from Odoo""",
    "author": "Bassam Infotech",
    "website": "http://www.bassaminfotech.in",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Uncategorized",
    "version": "15.0.0.1",
    "depends": ["stock", "stock_picking_batch", "delivery", "bi_inventory_generic_customisation"],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "report/report_header.xml",
        "report/report_paperformat.xml",
        "report/report_action.xml",
        "report/report_template.xml",
        "view/stock_picking_batch.xml",
        "view/zone_master.xml",
    ],
}
