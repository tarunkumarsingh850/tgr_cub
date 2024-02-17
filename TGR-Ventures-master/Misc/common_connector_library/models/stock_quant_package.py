# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    tracking_no = fields.Char("Additional Reference", help="This field is used for storing the tracking number.")
    weight_in_gram = fields.Float(string="Weight in Gram")

    @api.onchange("weight_in_gram")
    def onchange_weight_in_gram(self):
        if self.weight_in_gram:
            self.shipping_weight = (self.weight_in_gram) / 1000
