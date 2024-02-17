from odoo import models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_multi_register_payment(self):
        """Open the account.mulit.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.multi.payment.register wizard.
        """
        context = {
            "active_model": "account.move",
            "active_ids": self.ids,
        }
        selected_partner = self.mapped("partner_id.parent_id")
        if len(selected_partner) == 1:
            context.update(
                {
                    "default_partner_id": selected_partner.id,
                }
            )
        return {
            "name": _("Multiple Invoice Payment"),
            "res_model": "account.multi.payment.register",
            "view_mode": "form",
            "context": context,
            "target": "new",
            "type": "ir.actions.act_window",
        }


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_multi_reconciliation_partials(self, payments_to_do, writeoff_to_do, payment_date, move_type):
        r"""Prepare the partials on the current journal items to perform the reconciliation.
        /!\ The order of records in self is important because the journal items will be reconciled using this order.
        Copy of _prepare_reconciliation_partials method

        The only change we need to make here is for the amount used to create partial reconcile
        records. These values will be available in the payments_to_do dictionary. The credit amount
        residual and debit amount residual will be calculated based on the move_type

        TODO: add support for receipts

        :param payments_to_do: A dictionary with move_id as key and payment amount as value
        :param writeoff_to_do: A dictionary with move_id as key and writeoff amount as value
        :param payment_date: date of the payment
        :param move_type: type of account.move

        :return: A recordset of account.partial.reconcile.
        """
        debit_lines = iter(self.filtered(lambda line: line.balance > 0.0 or line.amount_currency > 0.0))
        credit_lines = iter(self.filtered(lambda line: line.balance < 0.0 or line.amount_currency < 0.0))
        debit_line = None
        credit_line = None

        debit_amount_residual = 0.0
        debit_amount_residual_currency = 0.0
        credit_amount_residual = 0.0
        credit_amount_residual_currency = 0.0
        debit_line_currency = None
        credit_line_currency = None

        partials_vals_list = []

        while True:

            # Move to the next available debit line.
            if not debit_line:
                debit_line = next(debit_lines, None)
                if not debit_line:
                    break
                if move_type in ("out_invoice", "in_refund"):
                    # For out_invoice, in_refund
                    # Use the sum of payment amount and writeoff amount as debit amount residual
                    if debit_line.currency_id.id == self.env.company.currency_id.id:
                        debit_amount_residual = payments_to_do[debit_line.move_id] + writeoff_to_do[debit_line.move_id]
                    # Convert to company currency if the move is in foreign currency.
                    else:
                        debit_amount_residual = debit_line.currency_id._convert(
                            payments_to_do[debit_line.move_id],
                            self.env.company.currency_id,
                            self.env.company,
                            payment_date,
                        ) + debit_line.currency_id._convert(
                            writeoff_to_do[debit_line.move_id],
                            self.env.company.currency_id,
                            self.env.company,
                            payment_date,
                        )
                else:
                    debit_amount_residual = debit_line.amount_residual

                if debit_line.currency_id:
                    if move_type in ("out_invoice", "in_refund"):
                        # For out_invoice, in_refund
                        debit_amount_residual_currency = (
                            payments_to_do[debit_line.move_id] + writeoff_to_do[debit_line.move_id]
                        )
                    else:
                        debit_amount_residual_currency = debit_line.amount_residual_currency
                    debit_line_currency = debit_line.currency_id
                else:
                    debit_amount_residual_currency = debit_amount_residual
                    debit_line_currency = debit_line.company_currency_id

            # Move to the next available credit line.
            if not credit_line:
                credit_line = next(credit_lines, None)
                if not credit_line:
                    break
                if move_type in ("in_invoice", "out_refund"):
                    # For in_invoice, out_refund
                    # Use the sum of payment amount and writeoff amount as credit amount residual (negative)
                    if debit_line.currency_id.id == self.env.company.currency_id.id:
                        credit_amount_residual = -(
                            payments_to_do[credit_line.move_id] + writeoff_to_do[credit_line.move_id]
                        )
                    # Convert to company currency if the move is in foreign currency.
                    else:
                        credit_amount_residual = -(
                            credit_line.currency_id._convert(
                                payments_to_do[credit_line.move_id],
                                self.env.company.currency_id,
                                self.env.company,
                                payment_date,
                            )
                            + credit_line.currency_id._convert(
                                writeoff_to_do[credit_line.move_id],
                                self.env.company.currency_id,
                                self.env.company,
                                payment_date,
                            )
                        )
                else:
                    credit_amount_residual = credit_line.amount_residual

                if credit_line.currency_id:
                    if move_type in ("in_invoice", "out_refund"):
                        # For in_invoice, out_refund
                        credit_amount_residual_currency = -(
                            payments_to_do[credit_line.move_id] + writeoff_to_do[credit_line.move_id]
                        )
                    else:
                        credit_amount_residual_currency = credit_line.amount_residual_currency
                    credit_line_currency = credit_line.currency_id
                else:
                    credit_amount_residual_currency = credit_amount_residual
                    credit_line_currency = credit_line.company_currency_id

            min_amount_residual = min(debit_amount_residual, -credit_amount_residual)
            has_debit_residual_left = (
                not debit_line.company_currency_id.is_zero(debit_amount_residual) and debit_amount_residual > 0.0
            )
            has_credit_residual_left = (
                not credit_line.company_currency_id.is_zero(credit_amount_residual) and credit_amount_residual < 0.0
            )
            has_debit_residual_curr_left = (
                not debit_line_currency.is_zero(debit_amount_residual_currency) and debit_amount_residual_currency > 0.0
            )
            has_credit_residual_curr_left = (
                not credit_line_currency.is_zero(credit_amount_residual_currency)
                and credit_amount_residual_currency < 0.0
            )

            if debit_line_currency == credit_line_currency:
                # Reconcile on the same currency.

                # The debit line is now fully reconciled.
                if not has_debit_residual_curr_left and (has_credit_residual_curr_left or not has_debit_residual_left):
                    debit_line = None
                    continue

                # The credit line is now fully reconciled.
                if not has_credit_residual_curr_left and (has_debit_residual_curr_left or not has_credit_residual_left):
                    credit_line = None
                    continue

                min_amount_residual_currency = min(debit_amount_residual_currency, -credit_amount_residual_currency)
                min_debit_amount_residual_currency = min_amount_residual_currency
                min_credit_amount_residual_currency = min_amount_residual_currency

            else:
                # Reconcile on the company's currency.

                # The debit line is now fully reconciled.
                if not has_debit_residual_left and (has_credit_residual_left or not has_debit_residual_curr_left):
                    debit_line = None
                    continue

                # The credit line is now fully reconciled.
                if not has_credit_residual_left and (has_debit_residual_left or not has_credit_residual_curr_left):
                    credit_line = None
                    continue

                min_debit_amount_residual_currency = credit_line.company_currency_id._convert(
                    min_amount_residual,
                    debit_line.currency_id,
                    credit_line.company_id,
                    credit_line.date,
                )
                min_credit_amount_residual_currency = debit_line.company_currency_id._convert(
                    min_amount_residual,
                    credit_line.currency_id,
                    debit_line.company_id,
                    debit_line.date,
                )

            debit_amount_residual -= min_amount_residual
            debit_amount_residual_currency -= min_debit_amount_residual_currency
            credit_amount_residual += min_amount_residual
            credit_amount_residual_currency += min_credit_amount_residual_currency

            partials_vals_list.append(
                {
                    "amount": min_amount_residual,
                    "debit_amount_currency": min_debit_amount_residual_currency,
                    "credit_amount_currency": min_credit_amount_residual_currency,
                    "debit_move_id": debit_line.id,
                    "credit_move_id": credit_line.id,
                }
            )

        return partials_vals_list

    def multi_reconcile(self, payments_to_do, writeoff_to_do, payment_date, move_type):
        """Reconcile the current move lines all together.
        Copy of reconcile method

        :param payments_to_do: A dictionary with move_id as key and payment amount as value
        :param writeoff_to_do: A dictionary with move_id as key and writeoff amount as value
        :param payment_date: date of the payment
        :param move_type: type of account.move

        :return: A dictionary representing a summary of what has been done during the reconciliation:
                * partials:             A recorset of all account.partial.reconcile created during the reconciliation.
                * full_reconcile:       An account.full.reconcile record created when there is nothing left to reconcile
                                        in the involved lines.
                * tax_cash_basis_moves: An account.move recordset representing the tax cash basis journal entries.
        """
        results = {}

        if not self:
            return results

        # List unpaid invoices
        not_paid_invoices = self.move_id.filtered(
            lambda move: move.is_invoice(include_receipts=True) and move.payment_state not in ("paid", "in_payment")
        )

        # ==== Check the lines can be reconciled together ====
        company = None
        account = None
        for line in self:
            if line.reconciled:
                raise UserError(_("You are trying to reconcile some entries that are already reconciled."))
            if not line.account_id.reconcile and line.account_id.internal_type != "liquidity":
                raise UserError(
                    _(
                        "Account %s does not allow reconciliation. First change the configuration of "
                        "this account to allow it."
                    )
                    % line.account_id.display_name
                )
            if line.move_id.state != "posted":
                raise UserError(_("You can only reconcile posted entries."))
            if company is None:
                company = line.company_id
            elif line.company_id != company:
                raise UserError(
                    _("Entries doesn't belong to the same company: %s != %s")
                    % (company.display_name, line.company_id.display_name)
                )
            if account is None:
                account = line.account_id
            elif line.account_id != account:
                raise UserError(
                    _("Entries are not from the same account: %s != %s")
                    % (account.display_name, line.account_id.display_name)
                )

        sorted_lines = self.sorted(key=lambda line: (line.date_maturity or line.date, line.currency_id))

        # ==== Collect all involved lines through the existing reconciliation ====

        involved_lines = sorted_lines
        involved_partials = self.env["account.partial.reconcile"]
        current_lines = involved_lines
        current_partials = involved_partials
        while current_lines:
            current_partials = (current_lines.matched_debit_ids + current_lines.matched_credit_ids) - current_partials
            involved_partials += current_partials
            current_lines = (current_partials.debit_move_id + current_partials.credit_move_id) - current_lines
            involved_lines += current_lines

        # ==== Create partials ====

        # Use _prepare_multi_reconciliation_partials instead of _prepare_reconciliation_partials
        partials = self.env["account.partial.reconcile"].create(
            sorted_lines._prepare_multi_reconciliation_partials(payments_to_do, writeoff_to_do, payment_date, move_type)
        )

        # Track newly created partials.
        results["partials"] = partials
        involved_partials += partials

        # ==== Create entries for cash basis taxes ====

        is_cash_basis_needed = account.user_type_id.type in ("receivable", "payable")
        if is_cash_basis_needed and not self._context.get("move_reverse_cancel"):
            tax_cash_basis_moves = partials._create_tax_cash_basis_moves()
            results["tax_cash_basis_moves"] = tax_cash_basis_moves

        # ==== Check if a full reconcile is needed ====

        if involved_lines[0].currency_id and all(
            line.currency_id == involved_lines[0].currency_id for line in involved_lines
        ):
            is_full_needed = all(line.currency_id.is_zero(line.amount_residual_currency) for line in involved_lines)
        else:
            is_full_needed = all(line.company_currency_id.is_zero(line.amount_residual) for line in involved_lines)

        if is_full_needed:

            # ==== Create the exchange difference move ====

            if self._context.get("no_exchange_difference"):
                exchange_move = None
            else:
                exchange_move = involved_lines._create_exchange_difference_move()
                if exchange_move:
                    exchange_move_lines = exchange_move.line_ids.filtered(lambda line: line.account_id == account)

                    # Track newly created lines.
                    involved_lines += exchange_move_lines

                    # Track newly created partials.
                    exchange_diff_partials = (
                        exchange_move_lines.matched_debit_ids + exchange_move_lines.matched_credit_ids
                    )
                    involved_partials += exchange_diff_partials
                    results["partials"] += exchange_diff_partials

                    exchange_move._post(soft=False)

            # ==== Create the full reconcile ====

            results["full_reconcile"] = self.env["account.full.reconcile"].create(
                {
                    "exchange_move_id": exchange_move and exchange_move.id,
                    "partial_reconcile_ids": [(6, 0, involved_partials.ids)],
                    "reconciled_line_ids": [(6, 0, involved_lines.ids)],
                }
            )

        # Trigger action for paid invoices
        not_paid_invoices.filtered(lambda move: move.payment_state in ("paid", "in_payment")).action_invoice_paid()

        return results
