from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    warehouse_ids = fields.Many2many("stock.warehouse", string="Warehouse")
