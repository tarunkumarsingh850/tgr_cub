from odoo import _, models, fields


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    date_from = fields.Datetime(string="Date From")
    date_to = fields.Datetime(string="Date From")

    def action_import_lines(self):
        return {
            "name": _("Import Bank Statement"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "transaction.line.wizard",
            "context": {"default_bank_statement_line_id": self.id},
            "target": "new",
        }
