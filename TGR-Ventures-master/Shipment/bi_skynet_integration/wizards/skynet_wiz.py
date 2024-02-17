from odoo import fields, models


class SkynetReportWiz(models.TransientModel):
    _name = "skynet.report.wiz"

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
        return self.env.ref("bi_skynet_integration.action_report_skynet").report_action(self, config=False)

    def get_picking_value(self):
        carrier_id = self.env["delivery.carrier"].search([("delivery_type", "=", "skynet")])
        domain = []
        if self.start_date:
            domain.append(("date_done", ">=", self.start_date))
        if self.end_date:
            domain.append(("date_done", "<=", self.end_date))
        domain.append(("state", "=", "done"))
        domain.append(("carrier_id", "in", carrier_id.ids))
        picking_id = self.env["stock.picking"].search(domain)
        return picking_id

    def get_picking_weight(self, picking):
        total_product_weight = 0
        for line in picking.move_ids_without_package:
            weight = 0
            if line.product_id.weight:
                weight = line.product_id.weight * line.product_uom_qty
            total_product_weight += weight
        return total_product_weight
