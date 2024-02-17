{
    "name": "Day-to-Day Inventory Forecast Analysis",
    "version": "14.0.2.0",
    "summary": "Creates Day-to-Day Forecast Report for Your Inventory",
    "description": """
Day-to-Day Inventory Forecast Analysis
======================================

This module creates day-to-day forecast report for your inventory


Keywords: Odoo Inventory Report, Odoo Stock Report, Odoo Warehouse Report, Odoo Forecast Report,
Odoo Stock Forecast Report, Odoo Inventory Forecast Report, Odoo Move Report,
Odoo Stock Move Report, Odoo Inventory Move Report, Odoo Moves Report, Odoo Stock Moves Report,
Odoo Inventory Moves Report, Odoo Inventory Analysis, Odoo Stock Analysis, Odoo Warehouse Analysis,
Odoo Forecast Analysis, Odoo Stock Forecast Analysis, Odoo Inventory Forecast Analysis,
Odoo Move Analysis, Odoo Stock Move Analysis, Odoo Inventory Move Analysis, Odoo Moves Analysis,
Odoo Stock Moves Analysis, Odoo Inventory Moves Analysis
""",
    "category": "Warehouse",
    "author": "MAC5",
    "contributors": ["MAC5"],
    "website": "https://apps.odoo.com/apps/modules/browse?author=MAC5",
    "depends": [
        "purchase",
        "sale_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/stock_forecast_analysis_views.xml",
        "views/product_template_views.xml",
        "views/product_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": ["static/description/banner.png"],
    "price": 119.99,
    "currency": "EUR",
    "support": "mac5_odoo@outlook.com",
    "license": "OPL-1",
}
