{
    "name": "Product Barcode Generator",
    "summary": """
        Generates EAN13 Standard Barcode for Product.""",
    "description": """
        Generates EAN13 Standard Barcode for Product.'
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "sale",
    "version": "15.0.1.0.0",
    "depends": ["stock", "product"],
    "data": [
        "views/product_view.xml",
    ],
    "external_dependencies": {"python": ["python-barcode"]},
}
