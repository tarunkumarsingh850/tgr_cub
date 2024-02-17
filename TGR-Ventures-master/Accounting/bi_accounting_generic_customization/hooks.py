from odoo import _
from odoo.addons.account.models.account_move import AccountMove
from odoo.exceptions import UserError

import re

# forbidden fields
INTEGRITY_HASH_MOVE_FIELDS = ("date", "journal_id", "company_id")


def post_load_hook():
    def write(self, vals):
        for move in self:
            if (
                move.restrict_mode_hash_table
                and move.state == "posted"
                and set(vals).intersection(INTEGRITY_HASH_MOVE_FIELDS)
            ):
                raise UserError(
                    _("You cannot edit the following fields due to restrict mode being activated on the journal: %s.")
                    % ", ".join(INTEGRITY_HASH_MOVE_FIELDS)
                )
            if (move.restrict_mode_hash_table and move.inalterable_hash and "inalterable_hash" in vals) or (
                move.secure_sequence_number and "secure_sequence_number" in vals
            ):
                raise UserError(_("You cannot overwrite the values ensuring the inalterability of the accounting."))
            # if (move.posted_before and 'journal_id' in vals and move.journal_id.id != vals['journal_id']):
            #     raise UserError(_('You cannot edit the journal of an account move if it has been posted once.'))
            # if (move.name and move.name != '/' and move.sequence_number not in (0, 1) and 'journal_id' in vals and move.journal_id.id != vals['journal_id']):
            #     raise UserError(_('You cannot edit the journal of an account move if it already has a sequence number assigned.'))

            # You can't change the date of a move being inside a locked period.
            if move.state == "posted" and "date" in vals and move.date != vals["date"]:
                move._check_fiscalyear_lock_date()
                move.line_ids._check_tax_lock_date()

            # You can't post subtract a move to a locked period.
            if "state" in vals and move.state == "posted" and vals["state"] != "posted":
                move._check_fiscalyear_lock_date()
                move.line_ids._check_tax_lock_date()

            if (
                move.journal_id.sequence_override_regex
                and vals.get("name")
                and vals["name"] != "/"
                and not re.match(move.journal_id.sequence_override_regex, vals["name"])
            ):
                if not self.env.user.has_group("account.group_account_manager"):
                    raise UserError(
                        _(
                            "The Journal Entry sequence is not conform to the current format. Only the Advisor can change it."
                        )
                    )
                move.journal_id.sequence_override_regex = False

        if self._move_autocomplete_invoice_lines_write(vals):
            res = True
        else:
            vals.pop("invoice_line_ids", None)
            res = super(
                AccountMove, self.with_context(check_move_validity=False, skip_account_move_synchronization=True)
            ).write(vals)

        # You can't change the date of a not-locked move to a locked period.
        # You can't post a new journal entry inside a locked period.
        if "date" in vals or "state" in vals:
            posted_move = self.filtered(lambda m: m.state == "posted")
            posted_move._check_fiscalyear_lock_date()
            posted_move.line_ids._check_tax_lock_date()

        if "state" in vals and vals.get("state") == "posted":
            for move in self.filtered(
                lambda m: m.restrict_mode_hash_table and not (m.secure_sequence_number or m.inalterable_hash)
            ).sorted(lambda m: (m.date, m.ref or "", m.id)):
                new_number = move.journal_id.secure_sequence_id.next_by_id()
                vals_hashing = {
                    "secure_sequence_number": new_number,
                    "inalterable_hash": move._get_new_hash(new_number),
                }
                res |= super(AccountMove, move).write(vals_hashing)

        # Ensure the move is still well balanced.
        if "line_ids" in vals and self._context.get("check_move_validity", True):
            self._check_balanced()

        self._synchronize_business_models(set(vals.keys()))

        return res

    AccountMove.write = write
