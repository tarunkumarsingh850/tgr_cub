from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Sale Order"


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    _description = "Sale Order Line"

    consignment_ids = fields.Many2many("purchase.order", string="Consignment")


# To store the quantity sold in PO a from particular SO
class SOLine(models.Model):
    _name = "so.line"

    po_id = fields.Many2one("purchase.order", string="PO")
    so_line_id = fields.Many2one("sale.order.line", string="Sale Line ID")
    so_sold_qty = fields.Integer("Sold Qty")
