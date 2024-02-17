{
    "name": "Product Vendor Import",
    "summary": """Update the vendor for products using excel import.""",
    "version": "15.0.0.1",
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "license": "AGPL-3",
    "depends": [
        "base",
        "product",
        "bi_barcode",
        "report_xlsx",
    ],
    "data": [
        "security/ir.model.access.csv",
        "reports/report.xml",
        "wizards/product_vendor_import_wizard.xml",
    ],
}
