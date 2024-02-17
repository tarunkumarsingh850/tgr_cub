from odoo import fields, models


class CorreosWizard(models.TransientModel):
    _name = "correos.wizard"
    _rec_name = "company_id"

    start_date = fields.Date(
        string="Start Date",
        default=fields.Date.context_today,
    )
    end_date = fields.Date(
        string="End Date",
        default=fields.Date.context_today,
    )

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
    )

    carrier_id = fields.Many2one(
        string="Carrier",
        comodel_name="delivery.carrier",
    )

    def pdf_logistics_report(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "start_date": self.start_date,
                "end_date": self.end_date,
                "company_id": self.company_id.id,
                "carrier_id": self.carrier_id.id,
            },
        }
        return self.env.ref("bi_correos_printout.action_correos_export_report").report_action(self, data, config=False)

    def pdf_logistics_excel_report(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "start_date": self.start_date,
                "end_date": self.end_date,
                "company_id": self.company_id.id,
                "carrier_id": self.carrier_id.id,
            },
        }
        return self.env.ref("bi_correos_printout.action_correos_export__excel_report").report_action(self, data=data)
