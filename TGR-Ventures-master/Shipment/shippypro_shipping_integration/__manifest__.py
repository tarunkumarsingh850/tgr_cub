{
    "name": "Shippypro Shipping Integration",
    "category": "Website",
    "author": "Vraja Technologies",
    "version": "14.0.17.12.2021",
    "summary": """""",
    "description": """Using Shippypro odoo Integration We export order to shippypro.
    amazon shipping, sendclound, ebay, shopify.""",
    "depends": ["delivery"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company.xml",
        "views/delivery_carrier.xml",
        "views/sale_order.xml",
        "views/stock_immediate_transfer_views.xml",
        "views/stock_picking.xml",
        "views/shippypro_carrier.xml",
        "views/stock_package_type.xml",
    ],
    "maintainer": "Vraja Technologies",
    "website": "https://www.vrajatechnologies.com",
    "images": ["static/description/cover.jpg"],
    "demo": [],
    "installable": True,
    "live_test_url": "https://www.vrajatechnologies.com/contactus",
    "application": True,
    "auto_install": False,
    "price": "279",
    "currency": "EUR",
    "license": "OPL-1",
}

# version changelog
# 14.0.30.03.2021 fix authentication issue , fix set service issue
# 14.0.04.10.2021 latest version
# 14.0.18.10.2021 customer create shipment without rate api service
# 14.0.27.10.2021 fix bug in import carrier
# 14.0.23.11.2021 Ben custom chages in shippypro rate service

# 14.0.8.12.2021
# create only shipping carrier service
