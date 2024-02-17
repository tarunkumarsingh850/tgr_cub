from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_id = fields.Many2one("sale.order", string="Sale")
