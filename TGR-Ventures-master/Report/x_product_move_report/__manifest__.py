{
    "name": "Product Activity",
    "summary": """
        Product Activity Report""",
    "description": """
        Product Activity Report
    """,
    "author": "Bassam Infotech LLP",
    "website": "http://www.bassaminfotech.com",
    "product": "Uncategorized",
    "version": "15.0.1",
    "license": "OPL-1",
    "depends": ["base", "stock", "report_xlsx"],
    "data": [
        "report/paperformat.xml",
        "report/product_report_pdf_view.xml",
        "report/report_action.xml",
        "security/ir.model.access.csv",
        "wizard/prod_activity_wizard.xml",
        "views/product_product.xml",
    ],
}
