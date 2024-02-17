from odoo import fields, models


class BarneysWizard(models.TransientModel):
    _name = "barneys.wizard"

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
    cost_percentage = fields.Integer(
        string="Cost %",
    )

    def export_excel_report(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "start_date": self.start_date,
                "end_date": self.end_date,
                "company_id": self.company_id.id,
                "cost_percentage": self.cost_percentage,
            },
        }
        return self.env.ref("bi_barneys_report.action_export_report").report_action(self, data, config=False)
