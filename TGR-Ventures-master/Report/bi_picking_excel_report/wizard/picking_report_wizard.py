from odoo import fields, models


class PickingReportWizard(models.TransientModel):
    _name = "picking.report.wizard"
    _description = "Wizard for picking report"

    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    date_start = fields.Date("Start Date")
    date_end = fields.Date("End Date")
    batch_id = fields.Many2one("stock.picking.batch", string="Batch")

    def generate_xlsx_report(self):

        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "warehouse_id": self.warehouse_id.id,
                "date_end": self.date_end,
                "date_start": self.date_start,
                "batch_id": self.batch_id.id,
            },
        }
        return self.env.ref("bi_picking_excel_report.action_picking_report").report_action(
            self, data=data, config=False
        )
