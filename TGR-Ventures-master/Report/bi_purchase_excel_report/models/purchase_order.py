from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_print_excel(self):
        data = {
            "ids": self.ids,
            "model": self._name,
        }
        return self.env.ref("bi_purchase_excel_report.action_view_purchase_order_excel1").report_action(
            self, data=data, config=False
        )
