from odoo import fields, models


class MagentoProductTemplate(models.Model):
    _inherit = "magento.product.template"

    retail_uk_price = fields.Float("Retail UK Price", related="odoo_product_template_id.retail_uk_price")
    retail_us_price = fields.Float("Retail US Price", related="odoo_product_template_id.retail_us_price")
    retail_default_price = fields.Float("Retail Default Price", related="odoo_product_template_id.retail_default_price")
    retail_special_price = fields.Float("Retail Special Price", related="odoo_product_template_id.retail_special_price")
    wholesale_special_price = fields.Float(
        "Wholesale Special Price", related="odoo_product_template_id.wholesale_special_price"
    )
    wholesale_price_value = fields.Float("Wholesale Price", related="odoo_product_template_id.wholesale_price_value")
    za_price = fields.Float("ZA Price", related="odoo_product_template_id.za_price")
    wholesale_special_us = fields.Float("Wholesale Special US", related="odoo_product_template_id.wholesale_special_us")
    wholesale_special_za = fields.Float("Wholesale Special ZA", related="odoo_product_template_id.wholesale_special_za")
    wholesale_special_uk = fields.Float("Wholesale Special UK", related="odoo_product_template_id.wholesale_special_uk")
    wholesale_us = fields.Float("Wholesale US", related="odoo_product_template_id.wholesale_us")
    wholesale_za = fields.Float("Wholesale ZA", related="odoo_product_template_id.wholesale_za")
    wholesale_uk = fields.Float("Wholesale UK", related="odoo_product_template_id.wholesale_uk")
    retail_special_us = fields.Float("Retail Special US", related="odoo_product_template_id.retail_special_us")
    retail_special_za = fields.Float("Retail Special ZA", related="odoo_product_template_id.retail_special_za")
    retail_special_uk = fields.Float("Retail Special UK", related="odoo_product_template_id.retail_special_uk")
    retail_za_price = fields.Float("Retail ZA Price", related="odoo_product_template_id.retail_za_price")
