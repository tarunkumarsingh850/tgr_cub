from odoo import models, fields


class ProductPriceHistory(models.Model):
    _name = "product.price.history"
    _description = "Product Price History"

    product_id = fields.Many2one("product.template", string="Product")
    date = fields.Datetime("Date")
    user_id = fields.Many2one("res.users", string="User")
    retail_uk_price = fields.Float("Retail UK Price", default=0.0)
    retail_us_price = fields.Float("Retail US Price", default=0.0)
    retail_default_price = fields.Float("Retail Default Price", default=0.0)
    retail_special_price = fields.Float("Retail Special Price", default=0.0)
    wholesale_special_price = fields.Float("Wholesale Special Price", default=0.0)
    wholesale_price_value = fields.Float("Wholesale Default EUR", default=0.0)
    za_price = fields.Float("ZA Price", default=0.0)
    wholesale_special_us = fields.Float("Wholesale Special US", default=0.0)
    wholesale_special_za = fields.Float("Wholesale Special ZA", default=0.0)
    wholesale_special_uk = fields.Float("Wholesale Special UK", default=0.0)
    wholesale_us = fields.Float("Wholesale US", default=0.0)
    wholesale_za = fields.Float("Wholesale ZA", default=0.0)
    wholesale_uk = fields.Float("Wholesale UK", default=0.0)
    retail_special_us = fields.Float("Retail Special US", default=0.0)
    retail_special_za = fields.Float("Retail Special ZA", default=0.0)
    retail_special_uk = fields.Float("Retail Special UK", default=0.0)
    retail_za_price = fields.Float("Retail ZA Price", default=0.0)
    is_send_to_magento = fields.Boolean("Is Send To Magento")
