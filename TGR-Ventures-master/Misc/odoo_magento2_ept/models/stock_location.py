from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    magento_location = fields.Char("Magento Location")
