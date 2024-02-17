from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_print_excel(self):
        data = {
            "ids": self.ids,
            "model": self._name,
        }
        return self.env.ref("bi_purchase_receipt_excel_report.action_view_purchase_receipt_excel1").report_action(
            self, data=data, config=False
        )
