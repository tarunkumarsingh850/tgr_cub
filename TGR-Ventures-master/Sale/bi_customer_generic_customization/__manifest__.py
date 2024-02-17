{
    "name": "Customer Master Generic Customization",
    "summary": """
        Customer Master Generic Customization""",
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Uncategorized",
    "version": "15.0.0.1",
    "depends": [
        "base",
        "account",
        "partner_manual_rank",
        "bi_vendor_generic_customisation",
        #"bi_inventory_generic_customisation",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/customer_class.xml",
        "views/bi_customer.xml",
        "views/res_config.xml",
    ],
}
