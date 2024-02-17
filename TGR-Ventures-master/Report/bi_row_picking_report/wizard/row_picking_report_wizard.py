from odoo import fields, models


class RowPickingReportWizard(models.TransientModel):
    _name = "row.picking.report.wizard"
    _description = "Rest of world order picking report wizard"

    # warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    date_start = fields.Date("Start Date")
    date_end = fields.Date("End Date")
    batch_id = fields.Many2one("stock.picking.batch", string="Batch")
    location_id = fields.Many2one("stock.location", "Location")

    def generate_xlsx_report(self):

        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "location_id": self.location_id.id,
                "date_end": self.date_end,
                "date_start": self.date_start,
                "batch_id": self.batch_id.id,
            },
        }
        return self.env.ref("bi_row_picking_report.action_row_picking_report").report_action(
            self, data=data, config=False
        )
