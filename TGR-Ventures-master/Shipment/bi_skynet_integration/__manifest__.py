{
    "name": "Skynet Shipping Integration",
    "summary": "Send shipment order to Skynet, track shipments on Skynet.",
    "version": "16.0.1.0",
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "license": "LGPL-3",
    "depends": ["base", "delivery", "sale", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings.xml",
        "views/delivery_carrier.xml",
        "views/stock_picking.xml",
        "reports/report_action.xml",
        "reports/report_header.xml",
        "reports/report_skynet.xml",
        "wizards/skynet_wiz.xml",
    ],
}
