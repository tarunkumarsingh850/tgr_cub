from odoo import _, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def export_template(self):
        return self.env.ref("bi_purchase_import.action_export_template").report_action(self, config=False)

    def export_lpo_template(self):
        return self.env.ref("bi_purchase_import.action_export_lpo_template").report_action(self, config=False)

    def action_import(self):
        return {
            "name": _("Import Lines"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "purchase.update.wizard",
            "context": {"default_purchase_update_id": self.id},
            "target": "new",
        }
