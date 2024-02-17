from odoo import models, fields


class BackorderReservedProductWizard(models.TransientModel):
    _name = "backorder.reserved.product.wizard"
    _description = "Backorder Reserved Product Wizard"

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    def print_backorder_reserved_product_report(self):
        data = {
            "start_date": self.start_date,
            "end_date": self.end_date,
        }
        return self.env.ref("bi_backorder_report.action_backorder_inventory_report").report_action(
            self, data, config=False
        )
