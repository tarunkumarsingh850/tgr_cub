{
    "name": "bi_barcode",
    "summary": "",
    "description": "",
    "author": "Bassam Infotech LLP",
    "website": "http://www.bassaminfotech.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "15.0.5",
    # any module necessary for this one to work correctly
    "license": "AGPL-3",
    "depends": ["base", "product", "stock"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/views.xml",
        "views/sequence.xml",
        "report/report_action.xml",
        "wizards/sale_price_update_wizard_views.xml",
        "wizards/update_price_wizard.xml",
        "wizards/updation_status_wizard.xml",
    ],
    "external_dependencies": {
        "python": ["xlrd"],
    },
}
