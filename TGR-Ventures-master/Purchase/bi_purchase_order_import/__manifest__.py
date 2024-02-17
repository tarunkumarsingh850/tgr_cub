{
    "name": "purchase_order_import",
    "summary": """
       Module is used to update the Purchase order.
    """,
    "description": """
       Module is used to update the Purchase order
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Purchase",
    "version": "15.0.1.0.1",
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "depends": ["purchase", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "report/report_action.xml",
        "wizard/purchase_order_wizard.xml",
    ],
}
