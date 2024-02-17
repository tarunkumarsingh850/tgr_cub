from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _description = "Stock Picking"

    is_drop_shipping = fields.Boolean(string="Is Drop Shipping")
