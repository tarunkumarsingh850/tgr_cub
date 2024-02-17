from odoo import fields, models, api


class StockPackageType(models.Model):
    _inherit = "stock.package.type"

    shippypro_carrier_id = fields.Many2one("shippypro.carrier", string="Shippypro Carrier")
    weight_in_gram = fields.Float(string="Weight in Gram")

    @api.onchange("weight_in_gram")
    def onchange_weight_in_gram(self):
        if self.weight_in_gram:
            self.max_weight = (self.weight_in_gram) / 1000
