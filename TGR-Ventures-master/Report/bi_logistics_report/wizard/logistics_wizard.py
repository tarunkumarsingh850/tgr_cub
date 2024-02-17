from odoo import fields, models


class LogisticsWizard(models.Model):
    _name = "logistics.wizard"
    _description = "Model is used to take logistics Report"

    start_date = fields.Date(string="Start Date", required=1)
    end_date = fields.Date(string="End Date", required=1)
    logistics_id = fields.Many2one(comodel_name="bi.logistics.master", string="Logistics", required=1)

    def export_logistics_report(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {"start_date": self.start_date, "end_date": self.end_date, "logistics_id": self.logistics_id.id},
        }
        return self.env.ref("bi_logistics_report.action_export_report").report_action(self, data, config=False)

    def pdf_logistics_report(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {"start_date": self.start_date, "end_date": self.end_date, "logistics_id": self.logistics_id.id},
        }
        return self.env.ref("bi_logistics_report.action_pdf_report").report_action(self, data, config=False)
