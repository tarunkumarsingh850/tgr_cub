{
    "name": "Dynamic Sale Report",
    "summary": """
        Dynamic Sale Report""",
    "description": """
        Dynamic Sale Report
    """,
    "author": "Bassam Infotech LLP",
    "website": "http://www.bassaminfotech.com",
    "product": "Uncategorized",
    "version": "15.0.1",
    "license": "OPL-1",
    "depends": ["base", "sale", "report_xlsx", "account", "web"],
    "data": [
        "security/ir.model.access.csv",
        "report/header.xml",
        "report/pdf_template.xml",
        "wizard/sale_report_wizard.xml",
        "report/sale_report_action.xml",
        "report/templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/bi_dynamic_sale_report/static/src/js/script.js",
        ],
        "web.assets_qweb": [
            "/bi_dynamic_sale_report/static/src/xml/view.xml",
        ],
    },
}
