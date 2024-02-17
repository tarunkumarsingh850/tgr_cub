from odoo import models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def reverse_moves(self):
        """
        inherit function for send email when user Add a credit note.
        Returns:

        """
        res = super(AccountMoveReversal, self).reverse_moves()
        new_move_ids = self.new_move_ids
        move_ids = self.move_ids
        if move_ids and move_ids.warehouse_id and move_ids.warehouse_id.is_credit_note_email:
            for move in new_move_ids:
                email_template = self.env.ref("bi_accounting_generic_customization.email_template_credit_note")
                email_template.email_from = "info@tiger-one.eu"
                email_template.send_mail(move.id, force_send=True)
        return res
