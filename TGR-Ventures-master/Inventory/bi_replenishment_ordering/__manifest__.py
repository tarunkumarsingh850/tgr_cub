{
    "name": "Stock Replenishment Ordering",
    "summary": """Get stock replenishment quantity suggestion
    and create purchase orders.""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "depends": [
        "base",
        "product",
        "stock",
        "bi_inventory_generic_customisation",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/replenishment_quantity_overview.xml",
    ],
}
