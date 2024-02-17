from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def button_print_excel(self):
        data = {
            "ids": self.ids,
            "model": self._name,
        }
        return self.env.ref("bi_sale_excel_report.action_view_sale_order_excel1").report_action(
            self, data=data, config=False
        )
