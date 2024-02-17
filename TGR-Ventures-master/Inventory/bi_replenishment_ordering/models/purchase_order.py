from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Purchase Order"

    replenishment_order_id = fields.Many2one("replenishment.quantity.overview", string="Replenishment Order")
