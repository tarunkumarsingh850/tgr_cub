from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_product_activity_report_html(self):
        report_action = self.env["product.activity.report"]
        return report_action.with_context({"product_id": self}).action_product_report()
