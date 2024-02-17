from odoo import models, fields, api, _
from datetime import datetime


class BreederReportWizard(models.Model):
    _name = "breeder.report.wizard"

    brand_id = fields.Many2many("product.breeder", string="Brand")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")

    def action_print_breeder_report(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "brand_id": self.brand_id,
                "warehouse_id" : self.warehouse_id,
            },
        }
        return self.env.ref("bi_breeder_report.report_brand_breeder_xlsx").report_action(
            self, data=data, config=False
        )

