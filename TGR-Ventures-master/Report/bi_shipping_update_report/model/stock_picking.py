from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_export_template(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {"ids": self.ids},
        }
        return self.env.ref("bi_shipping_update_report.action_export_template").report_action(
            self, data=data, config=False
        )
