from odoo import _, fields, models
from odoo.exceptions import UserError


class PickingAssignWizard(models.TransientModel):
    _name = "bi.picking.wizard"

    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    picker_ids = fields.Many2many("res.users", string="Picker")
    warehouse_ids = fields.Many2many("stock.warehouse", string="Warehouse")

    def get_report_xlsx(self):

        if self.date_start > self.date_end:
            raise UserError(_("End Date must be larger than Start Date"))
        else:
            data = {
                "model": self._name,
                "ids": self.ids,
                "form": {
                    "date_start": self.date_start,
                    "date_end": self.date_end,
                    "picker_ids": self.picker_ids.ids,
                    "warehouse_ids": self.warehouse_ids.ids,
                },
            }
            return self.env.ref("bi_picking_assign_report.picking_wizard_report_excel").report_action(
                self, data=data, config=False
            )
