from odoo import models, fields


class InventoryLogisticWizard(models.Model):
    _name = "inventory.logistic.wizard"
    _description = "Inventory Logistic Wizard"

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    def print_inventory_logistic_report(self):
        data = {
            "start_date": self.start_date,
            "end_date": self.end_date,
        }
        return self.env.ref("bi_inventory_logistic_report.action_export_inventory_logistic_report").report_action(
            self, data, config=False
        )
