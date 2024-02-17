from odoo import _, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_import_invoice_line(self):
        return {
            "name": _("Import Invoice Lines"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "invoice.line.wizard",
            "context": {"default_invoice_line_update_id": self.id},
            "target": "new",
        }
