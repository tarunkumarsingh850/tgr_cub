from odoo import fields, models


class ConsignmentWizard(models.Model):
    _name = "bi.consignment.wizard"
    _description = "XLS Report for Consignment Records"

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    po_ids = fields.Many2many(
        "purchase.order",
        string="Purchase Order",
        domain=[("is_consignment_order", "=", True), ("state", "in", ["done", "purchase"])],
    )
    cost_percentage = fields.Integer("Cost %")

    def export_xls_report(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "start_date": self.start_date,
                "end_date": self.end_date,
                "po_ids": self.po_ids.ids,
                "cost_percentage": self.cost_percentage,
            },
        }
        return self.env.ref("bi_consignment_report.action_bi_consignment_xl_report").report_action(
            self, data=data, config=False
        )
