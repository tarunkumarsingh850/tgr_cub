from odoo import fields, models


class MrwReportWiz(models.TransientModel):
    _name = "mrw.report.wiz"

    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company)

    def print_report(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "start_date": self.start_date,
                "end_date": self.end_date,
            },
        }
        return self.env.ref("bi_mrw_report.action_report_mrw").report_action(self, config=False)

    def get_picking_value(self):
        carrier_id = self.env["delivery.carrier"].search([("delivery_type", "=", "mrw_vts")])
        domain = []
        if self.start_date:
            domain.append(("date_done", ">=", self.start_date))
        if self.end_date:
            domain.append(("date_done", "<=", self.end_date))
        domain.append(("state", "=", "done"))
        domain.append(("carrier_id", "in", carrier_id.ids))
        picking_id = self.env["stock.picking"].search(domain)
        return picking_id
