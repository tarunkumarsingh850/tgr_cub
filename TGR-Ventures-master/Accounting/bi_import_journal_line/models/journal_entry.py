from odoo import _, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_import_line(self):
        return {
            "name": _("Import Lines"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "journal.line.wizard",
            "context": {"default_journal_line_update_id": self.id},
            "target": "new",
        }
