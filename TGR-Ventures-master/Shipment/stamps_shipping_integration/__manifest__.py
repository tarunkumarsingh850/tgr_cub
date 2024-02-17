{
    "name": "Stamps.com(USPS) Shipping Integration",
    "category": "Website",
    "author": "Vraja Technologies",
    "version": "15.0.29.12.21",
    "summary": """""",
    "description": """We are providing following modules, Shipping Operations, shipping, odoo shipping integration,odoo shipping connector, dhl express, fedex, ups, gls, usps, stamps.com, shipstation, bigcommerce, easyship, amazon shipping, sendclound, ebay, shopify.""",
    "depends": ["delivery", "bi_barneys_ecommerce_api", "odoo_ecommerce_api"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company.xml",
        "views/delivery_carrier_view.xml",
        "views/stock_picking_vts.xml",
        "views/sale_order.xml",
    ],
    "images": ["static/description/cover.png"],
    "maintainer": "Vraja Technologies",
    "website": "https://www.vrajatechnologies.com",
    "demo": [],
    "live_test_url": "https://www.vrajatechnologies.com/contactus",
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": "179",
    "currency": "EUR",
    "license": "OPL-1",
}
# 15.0 initial version
# 15.0.10.12.21 check is_instance in rate method
# 15.0.29.12.21 IntegratorTxID (picking.origin)
