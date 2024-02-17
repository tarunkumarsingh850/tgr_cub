from odoo import fields, models, _
from odoo.exceptions import UserError


class SaleSummaryReportWizard(models.TransientModel):
    _name = "sale.summary.report"

    def _check_dates(self, date_from, date_to):
        if date_from > date_to:
            raise UserError(_("Start-date must be lower than End-date"))
        return True

    date = fields.Date("Date", required=True)
    to_date = fields.Date('To Date', required=True)

    def action_view(self):
        res = {
            "type": "ir.actions.client",
            "name": "Sale Report",
            "tag": "category_wise_report",
            "context": {"wizard_id": self.id},
        }
        return res

    def export_xls(self):
        # self._check_dates(self.date_from, self.date_to)
        context = self._context
        datas = {"ids": context.get("active_ids", [])}
        datas["form"] = self.read()[0]
        for field in datas["form"].keys():
            if isinstance(datas["form"][field], tuple):
                datas["form"][field] = datas["form"][field][0]
        return self.env.ref("bi_sale_summary_report.sale_summary_report_wizard").report_action(
            self, data=datas, config=False
        )

    def export_pdf(self):
        self._check_dates(self.date_from, self.date_to)
        context = self._context
        datas = {"ids": context.get("active_ids", [])}
        datas["form"] = self.read()[0]
        for field in datas["form"].keys():
            if isinstance(datas["form"][field], tuple):
                datas["form"][field] = datas["form"][field][0]
        return self.env.ref("bi_sale_summary_report.sale_summary_report_pdf").report_action(
            self, data=datas, config=False
        )
