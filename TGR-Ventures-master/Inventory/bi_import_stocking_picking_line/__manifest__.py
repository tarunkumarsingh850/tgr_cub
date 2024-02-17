{
    "name": "Stock picking lines import",
    "summary": """
       Module is used to update the Stock picking lines import.
    """,
    "description": """
       Module is used to update the Stock picking lines import
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "stock",
    "version": "15.0.1.0.1",
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "depends": ["stock", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking.xml",
        "wizard/stock_picking_wizard.xml",
    ],
}
