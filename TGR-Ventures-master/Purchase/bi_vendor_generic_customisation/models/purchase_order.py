from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    description = fields.Text(string="Description")
