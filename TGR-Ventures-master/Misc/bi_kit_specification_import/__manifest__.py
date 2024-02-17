{
    "name": "Import Kit Specification",
    "summary": """
       Import Kit Specification
    """,
    "description": """
       Import Kit Specification
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "LGPL-3",
    "category": "Purchase",
    "version": "15.0.1.0.1",
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "depends": ["bi_kit_assembly", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/import_wizard.xml",
        "report/report_action.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bi_kit_specification_import/static/src/js/kit_tree_button.js",
        ],
        "web.assets_qweb": [
            "bi_kit_specification_import/static/src/xml/kit_tree_button.xml",
        ],
    },
}
