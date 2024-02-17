{
    "name": "bi_shipment_update_report",
    "summary": "Shipment tracking reference update",
    "description": "",
    "author": "Bassam Infotech LLP",
    "website": "http://www.bassaminfotech.com",
    "category": "Uncategorized",
    "version": "15.0.1",
    "license": "AGPL-3",
    "depends": ["base", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/update_shipment_tracking.xml",
        "report/report_action.xml",
        "view/stock_picking.xml",
    ],
    "external_dependencies": {
        "python": ["xlrd"],
    },
    "assets": {
        "web.assets_backend": [
            "bi_shipping_update_report/static/src/js/track_tree_button.js",
        ],
        "web.assets_qweb": [
            "bi_shipping_update_report/static/src/xml/track_tree_button.xml",
        ],
    },
}
