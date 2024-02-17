from odoo import fields, models, _
from odoo.exceptions import UserError


class UKTaxWizard(models.TransientModel):
    _name = "uk.tax.wizard"

    def _check_dates(self, date_from, date_to):
        if date_from > date_to:
            raise UserError(_("Start-date must be lower than End-date"))
        return True

    date_from = fields.Date("Start Date", required=True)
    date_to = fields.Date("End Date", required=True)
    tax_type = fields.Selection(string="Type", selection=[("sale", "Sale"), ("purchase", "Purchase")], required=True)

    def generate_xlsx_report(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {"start_date": self.date_from, "end_date": self.date_to, "tax_type": self.tax_type},
        }
        return self.env.ref("bi_uk_tax_report.report_uk_tax_report_xlsx").report_action(self, data=data, config=False)
