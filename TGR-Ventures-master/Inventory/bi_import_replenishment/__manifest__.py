{
    "name": "Import Replenishment",
    "summary": """
        Import Replenishment""",
    "description": """
        Import Replenishment
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Uncategorized",
    "version": "0.1",
    "depends": ["base", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/wizard.xml",
        "report/report_action.xml",
        "view/view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bi_import_replenishment/static/src/js/tree_button.js",
        ],
        "web.assets_qweb": [
            "bi_import_replenishment/static/src/xml/tree_button.xml",
        ],
    },
}
