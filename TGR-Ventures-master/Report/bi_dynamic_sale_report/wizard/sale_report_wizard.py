from odoo import fields, models, _
from odoo.exceptions import UserError


class DynamicWiseSaleWizard(models.TransientModel):
    _name = "dynamic.sale.report"

    def _check_dates(self, date_from, date_to):
        if date_from > date_to:
            raise UserError(_("Start-date must be lower than End-date"))
        return True

    date_from = fields.Date("Start Date", required=True)
    date_to = fields.Date("End Date", required=True)
    is_all = fields.Boolean("Is All", default=True)

    partner_id = fields.Many2one(
        string="Customer",
        comodel_name="res.partner",
    )
    cost_percentage = fields.Integer(
        string="Cost %",
    )

    def action_view(self):
        res = {
            "type": "ir.actions.client",
            "name": "Sale Report",
            "tag": "category_wise_report",
            "context": {"wizard_id": self.id},
        }
        return res

    def export_xls(self):
        self._check_dates(self.date_from, self.date_to)
        context = self._context
        datas = {"ids": context.get("active_ids", [])}
        datas["form"] = self.read()[0]
        for field in datas["form"].keys():
            if isinstance(datas["form"][field], tuple):
                datas["form"][field] = datas["form"][field][0]
        return self.env.ref("bi_dynamic_sale_report.sale_report_wizard").report_action(self, data=datas, config=False)

    def export_pdf(self):
        self._check_dates(self.date_from, self.date_to)
        context = self._context
        datas = {"ids": context.get("active_ids", [])}
        datas["form"] = self.read()[0]
        for field in datas["form"].keys():
            if isinstance(datas["form"][field], tuple):
                datas["form"][field] = datas["form"][field][0]
        return self.env.ref("bi_dynamic_sale_report.sale_report_pdf").report_action(self, data=datas, config=False)
