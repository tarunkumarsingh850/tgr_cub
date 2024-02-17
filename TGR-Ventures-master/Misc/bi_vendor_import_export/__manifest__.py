{
    "name": "Bi Vendor Import Export",
    "summary": "Module contains the import export funtions of vendor",
    "version": "15.0.0.1",
    "author": "Bassam Infotech LLP",
    "website": "https://www.bassaminfotech.com",
    "license": "LGPL-3",
    "depends": ["purchase", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "views/report_action.xml",
        "wizard/import_vendor.xml",
        "views/menu_views.xml",
    ],
    "images": [
        "static/description/icon.png",
    ],
    "demo": [],
    "external_dependencies": {
        "python": ["xlrd"],
    },
    "installable": True,
    "auto_install": False,
}
