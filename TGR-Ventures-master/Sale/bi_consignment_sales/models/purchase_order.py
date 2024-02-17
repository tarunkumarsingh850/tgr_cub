from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Purchase Order"

    is_consignment_order = fields.Boolean("Is Consignment Order", copy=False)
    is_consignment_used = fields.Boolean("Is Consignment Used", compute="_compute_consigment_used", store=True)
    so_line_ids = fields.One2many("so.line", "po_id", string="Sale Line")

    @api.depends("order_line.qty_received", "order_line.quantity_sold")
    def _compute_consigment_used(self):
        for order in self:
            if order.is_consignment_order and all(line.qty_received == line.quantity_sold for line in order.order_line):
                order.is_consignment_used = True
            else:
                order.is_consignment_used = False


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    _description = "Purchase Order Line"

    quantity_sold = fields.Float("Quantity Sold", copy=False)
