{
    "name": "bi_magento_attribute_import",
    "summary": "Module to Import Magento Other Attributes",
    "description": "",
    "author": "Bassam Infotech LLP",
    "website": "http://www.bassaminfotech.com",
    # for the full list
    "category": "Inventory",
    "version": "15.0.5",
    # any module necessary for this one to work correctly
    "license": "AGPL-3",
    "depends": ["product", "bi_barcode", "report_xlsx", "odoo_magento2_ept"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "report/report_action.xml",
        "views/magento_attribute.xml",
        "views/product_template.xml",
        "wizards/magento_attribute_update.xml",
        "views/attribute_master_view.xml"
    ],
}
