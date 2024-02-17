{
    "name": "bi_update_product_tracking",
    "summary": "bi_update_product_tracking",
    "description": "",
    "author": "Bassam Infotech LLP",
    "website": "http://www.bassaminfotech.com",
    "category": "Uncategorized",
    "version": "15.0.1",
    "license": "AGPL-3",
    "depends": ["base", "product", "stock", "bi_barcode"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/update_product_tracking.xml",
    ],
    "external_dependencies": {
        "python": ["xlrd"],
    },
}
