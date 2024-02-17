from odoo import fields, models, _
from odoo.exceptions import UserError


class ProductActivityWizard(models.TransientModel):
    _name = "product.activity.report"

    def _check_dates(self, date_from, date_to):
        if date_from and date_to and date_from > date_to:
            raise UserError(_("Start-date must be lower than End-date"))
        return True

    date_from = fields.Date("Start Date")
    date_to = fields.Date("End Date")
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
    )
    location_id = fields.Many2one("stock.location")

    def export_xls_cos(self):
        self._check_dates(self.date_from, self.date_to)
        context = self._context
        datas = {"ids": context.get("active_ids", [])}
        datas["form"] = self.read()[0]
        # for field in datas["form"].keys():
        #     if isinstance(datas["form"][field], tuple):
        #         datas["form"][field] = datas["form"][field][0]
        return self.env.ref("x_product_move_report.product_act_report_id").report_action(self, data=datas, config=False)

    def action_product_report(self):
        if self._context.get("product_id"):
            product_tmpl_id = self._context.get("product_id").id
            product_id = self.env["product.product"].search([("product_tmpl_id", "=", product_tmpl_id)])
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "date_from": self.date_from,
                "date_to": self.date_to,
                "product_id": self.product_id.id or product_id.id,
                "location_id": self.location_id.id,
            },
        }
        return self.env.ref("x_product_move_report.action_product_html").report_action(self, data=data)
