{
    "name": "purchase_update",
    "summary": """
       Module is used to update the Purchase.
    """,
    "description": """
       Module is used to update the Purchase
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
        # "data/sequence.xml",
        "security/ir.model.access.csv",
        "views/purchase_order.xml",
        "report/report_action.xml",
        "wizard/purchase_wizard.xml",
    ],
}
