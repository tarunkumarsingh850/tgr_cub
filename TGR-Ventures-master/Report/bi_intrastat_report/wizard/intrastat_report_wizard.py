from odoo import fields, models


class IntrastatReportWizard(models.TransientModel):
    _name = "intrastat.report.wizard"
    _description = "Wizard for Intrastat report"

    date_start = fields.Date("Start Date", required="1")
    date_end = fields.Date("End Date", required="1")
    move_type = fields.Selection(string="Type", selection=[("arrival", "Arrival"), ("dispatch", "Dispatch")])

    def generate_xlsx_report(self):

        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "date_end": self.date_end,
                "date_start": self.date_start,
                "move_type": self.move_type,
            },
        }
        return self.env.ref("bi_intrastat_report.action_intrastat_report").report_action(self, data=data, config=False)
