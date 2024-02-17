from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Purchase Order"

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for line in self.order_line:
            line.product_id.product_tmpl_id.last_cost_2 = line.price_unit
        return res
