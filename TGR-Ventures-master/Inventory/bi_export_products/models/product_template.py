from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_export_template(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {"ids": self.ids},
        }
        return self.env.ref("bi_export_products.action_export_template").report_action(self, data=data, config=False)
