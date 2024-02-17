from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res["customer_order"] = self.customer_order
        return res
