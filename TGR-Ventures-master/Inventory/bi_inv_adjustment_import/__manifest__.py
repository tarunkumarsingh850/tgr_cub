{
    "name": "Import Inventory Adjustment",
    "summary": """
      Import Inventory Adjustment
    """,
    "description": """
       Import Inventory Adjustment
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "",
    "version": "15.0.1.0.1",
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "depends": ["stock", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "report/report_action.xml",
        "view/view.xml",
        "wizard/wizard.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bi_inv_adjustment_import/static/src/js/tree_button.js",
        ],
        "web.assets_qweb": [
            "bi_inv_adjustment_import/static/src/xml/tree_button.xml",
        ],
    },
}
