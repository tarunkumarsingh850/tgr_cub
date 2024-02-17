{
    "name": "bi_ez_invoice_import",
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
    "depends": ["base", "account"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "report/report_action.xml",
        "wizard/ez_inoive_import_wizard_views.xml",
        "views/res_partner.xml"
    ],
}
