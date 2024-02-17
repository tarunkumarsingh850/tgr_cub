from odoo import fields, models


class StockMoveKit(models.Model):
    _inherit = "stock.move"

    assembly_id = fields.Many2one("kit.assembly", string="Kit Assembly")
