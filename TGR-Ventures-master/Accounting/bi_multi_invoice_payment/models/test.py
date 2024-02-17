from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMultiPaymentRegister(models.TransientModel):
    _name = "account.multi.payment.register"
    _description = "Multiple Payment Register"
    """
    We are making a copy of account.payment.register and then applying our
    customizations on top of this. This way we can make sure that the default
    odoo payment wizard works fine and our customization works like an addon.

    TODO: add cross-currency payment support
    TODO: add amount_total conditions

    """

    # == Business fields ==
    payment_date = fields.Date(string="Payment Date", required=True, default=fields.Date.context_today)
    amount = fields.Monetary(
        currency_field="currency_id",
        store=True,
        readonly=False,
        compute="_compute_amount",
        string="Payment Amount",
    )
    communication = fields.Char(string="Memo", store=True, readonly=False, compute="_compute_communication")
    group_payment = fields.Boolean(
        string="Group Payments",
        store=True,
        readonly=False,
        copy=False,
        compute="_compute_group_payment",
        help="Only one payment will be created by partner (bank)/ currency.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        store=True,
        readonly=False,
        compute="_compute_currency_id",
        help="The payment's currency.",
    )
    journal_id = fields.Many2one(
        "account.journal",
        store=True,
        readonly=False,
        compute="_compute_journal_id",
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]",
    )
    partner_bank_id = fields.Many2one(
        "res.partner.bank",
        string="Recipient Bank Account",
        readonly=False,
        store=True,
        compute="_compute_partner_bank_id",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), " "('partner_id', '=', partner_id)]",
    )
    company_currency_id = fields.Many2one("res.currency", string="Company Currency", related="company_id.currency_id")

    # == Fields given through the context ==
    line_ids = fields.Many2many(
        "account.move.line",
        "account_multi_payment_register_move_line_rel",
        "wizard_id",
        "line_id",
        string="Journal items",
        readonly=True,
        copy=False,
    )
    payment_type = fields.Selection(
        [
            ("outbound", "Send Money"),
            ("inbound", "Receive Money"),
        ],
        string="Payment Type",
        store=True,
        copy=False,
        compute="_compute_from_lines",
    )
    partner_type = fields.Selection(
        [
            ("customer", "Customer"),
            ("supplier", "Vendor"),
        ],
        store=True,
        copy=False,
        compute="_compute_from_lines",
    )
    source_amount = fields.Monetary(
        string="Amount to Pay (company currency)",
        store=True,
        copy=False,
        currency_field="company_currency_id",
        compute="_compute_from_lines",
    )
    source_amount_currency = fields.Monetary(
        string="Amount to Pay (foreign currency)",
        store=True,
        copy=False,
        currency_field="source_currency_id",
        compute="_compute_from_lines",
    )
    source_currency_id = fields.Many2one(
        "res.currency",
        string="Source Currency",
        store=True,
        copy=False,
        compute="_compute_from_lines",
        help="The payment's currency.",
    )
    can_edit_wizard = fields.Boolean(
        store=True,
        copy=False,
        compute="_compute_from_lines",
        help="Technical field used to indicate the user can edit the wizard content such as the amount.",
    )
    can_group_payments = fields.Boolean(
        store=True,
        copy=False,
        compute="_compute_from_lines",
        help="Technical field used to indicate the user can see the 'group_payments' box.",
    )
    company_id = fields.Many2one("res.company", store=True, copy=False, compute="_compute_from_lines")
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer/Vendor",
        store=True,
        copy=False,
        ondelete="restrict",
        compute="_compute_from_lines",
    )

    # == Payment methods fields ==
    payment_method_id = fields.Many2one(
        "account.payment.method",
        string="Payment Method",
        readonly=False,
        store=True,
        compute="_compute_payment_method_id",
        domain="[('id', 'in', available_payment_method_ids)]",
        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n"
        "Electronic: Get paid automatically through a payment acquirer by requesting "
        "a transaction on a card saved by the customer when buying or subscribing "
        "online (payment token).\n"
        "Check: Pay bill by check and print it from Odoo.\n"
        "Batch Deposit: Encase several customer checks at once by generating a "
        "batch deposit to submit to your bank. When encoding the bank statement in "
        "Odoo, you are suggested to reconcile the transaction with the batch "
        "deposit.To enable batch deposit, module account_batch_payment must "
        "be installed.\n"
        "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit"
        " to your bank. To enable sepa credit transfer, module account_sepa must "
        "be installed ",
    )
    available_payment_method_ids = fields.Many2many("account.payment.method", compute="_compute_payment_method_fields")
    hide_payment_method = fields.Boolean(
        compute="_compute_payment_method_fields",
        help="0 field used to hide the payment method if the selected journal has only one available which is 'manual'",
    )

    # == Payment difference fields ==
    payment_difference = fields.Monetary(compute="_compute_payment_difference")
    payment_difference_handling = fields.Selection(
        [
            ("open", "Keep open"),
            ("reconcile", "Mark as fully paid"),
        ],
        default="open",
        string="Payment Difference Handling",
        compute="_compute_payment_difference",
    )
    writeoff_account_id = fields.Many2one(
        "account.account",
        string="Difference Account",
        copy=False,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
    )
    writeoff_label = fields.Char(
        string="Journal Item Label",
        default="Write-Off",
        help="Change label of the counterpart that will hold the payment difference",
    )

    # == Display purpose fields ==
    show_partner_bank_account = fields.Boolean(
        compute="_compute_show_require_partner_bank",
        help="Technical field used to know whether the field `partner_bank_id` needs to be displayed or "
        "not in the payments form views",
    )
    require_partner_bank_account = fields.Boolean(
        compute="_compute_show_require_partner_bank",
        help="Technical field used to know whether the field `partner_bank_id` needs to be required or not in"
        " the payments form views",
    )
    country_code = fields.Char(related="company_id.country_id.code", readonly=True)

    # == Bassam Fields ==

    register_line_ids = fields.One2many(
        "account.multi.payment.register.line",
        "account_multi_payment_register_id",
        string="Payment Register Lines",
        store=True,
    )
    is_initial = fields.Boolean(string="Is Initial?", default=False, store=True)
    amount_total = fields.Monetary(string="Total Amount", currency_field="currency_id", store=True)
    move_type = fields.Selection(
        [
            ("out_invoice", "Customer Invoice"),
            ("out_refund", "Customer Credit Note"),
            ("in_invoice", "Vendor Bill"),
            ("in_refund", "Vendor Credit Note"),
        ],
        string="Move Type",
    )

    # == Bassam Methods ==

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        for record in self:
            # If the onchange is not getting triggered for the first time, add the open invoices against the partner
            if not record.is_initial:
                if record.partner_id:
                    move_ids = self.env["account.move"].search(
                        [
                            ("partner_id", "=", record.partner_id.id),
                            ("move_type", "=", record.move_type),
                            ("state", "=", "posted"),
                            ("payment_state", "in", ("not_paid", "partial")),
                        ],
                        order="invoice_date_due, date",
                    )
                    line_values = []
                    for each_move in move_ids:
                        values = (
                            0,
                            0,
                            {
                                "move_id": each_move.id,
                                "amount_payment": 0.0,
                                "partner_id": each_move.partner_id.id,
                            },
                        )
                        line_values.append(values)
                    # Write the new values after unlinking existing lines
                    record.register_line_ids.unlink()

                    # Odoo 14 onwards, the lines are stored in the wizard itself.
                    # Let us find the new move lines to reconcile since the partner has changed.
                    # Use the same process used by Odoo in default_get to find the lines
                    lines = move_ids.line_ids
                    available_lines = self.env["account.move.line"]
                    for line in lines:
                        if line.move_id.state != "posted":
                            raise UserError(_("You can only register payment for posted journal entries."))

                        if line.account_internal_type not in ("receivable", "payable"):
                            continue
                        if line.currency_id:
                            if line.currency_id.is_zero(line.amount_residual_currency):
                                continue
                        else:
                            if line.company_currency_id.is_zero(line.amount_residual):
                                continue
                        available_lines |= line

                    # Check.
                    if not available_lines:
                        raise UserError(
                            _(
                                "You can't register a payment from here because there is no due amount "
                                "for this partner."
                            )
                        )
                    if len(lines.company_id) > 1:
                        raise UserError(_("You can't create payments for entries belonging to different companies."))
                    if len(set(available_lines.mapped("account_internal_type"))) > 1:
                        raise UserError(
                            _(
                                "You can't register payments for journal items being either all inbound, either "
                                "all outbound."
                            )
                        )

                    record.update(
                        {
                            "register_line_ids": line_values,
                            "group_payment": True,
                            "line_ids": available_lines.ids,
                        }
                    )
                else:
                    # If there is no partner, unlink all the lines.
                    # For some reason partner_id and is_initial is getting reset. So set both of them as False
                    # TODO: Check whether above issue is fixable
                    record.register_line_ids.unlink()
                    record.update(
                        {
                            "partner_id": False,
                            "is_initial": False,
                        }
                    )
            # onchange is getting triggered for the first time, so add the invoices in context to the lines
            else:
                active_ids = self._context.get("active_ids")
                if active_ids:
                    move_ids = self.env["account.move"].search(
                        [("id", "in", active_ids)], order="invoice_date_due, date"
                    )
                    line_values = []
                    for each_move in move_ids:
                        values = (
                            0,
                            0,
                            {
                                "move_id": each_move.id,
                                "amount_payment": 0.0,
                                "partner_id": each_move.partner_id.id,
                            },
                        )
                        line_values.append(values)
                    record.update(
                        {
                            "register_line_ids": line_values,
                            "group_payment": len(move_ids) > 1 and record.is_initial,
                            "is_initial": False,
                        }
                    )

    @api.onchange("amount_total")
    def _onchange_amount_total(self):
        for record in self:
            if sum(record.register_line_ids.mapped("amount_residual")) < record.amount_total:
                record.amount_total = 0
                record.register_line_ids.amount_payment = 0
                record.amount = record.amount_total
            if record.amount_total > 0:
                total_amount = record.amount_total
                for each_line in record.register_line_ids:
                    if each_line.amount_residual <= total_amount:
                        each_line.amount_payment = each_line.amount_residual
                        total_amount -= each_line.amount_payment
                    elif each_line.amount_residual > total_amount:
                        each_line.amount_payment = total_amount
                        if total_amount > 0:
                            total_amount -= each_line.amount_payment
                record.amount = record.amount_total

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    @api.model
    def _get_batch_communication(self, batch_result):
        """Helper to compute the communication based on the batch.
        :param batch_result:    A batch returned by '_get_batches'.
        :return:                A string representing a communication to be set on payment.
        """
        labels = {line.name or line.move_id.ref or line.move_id.name for line in batch_result["lines"]}
        return " ".join(sorted(labels))

    @api.model
    def _get_line_batch_key(self, line):
        """Turn the line passed as parameter to a dictionary defining on which way the lines
        will be grouped together.
        :return: A python dictionary.
        """

        return {
            "partner_id": line.partner_id.id,
            "account_id": line.account_id.id,
            "currency_id": (line.currency_id or line.company_currency_id).id,
            "partner_bank_id": (line.move_id.partner_bank_id or line.partner_id.commercial_partner_id.bank_ids[:1]).id,
            "partner_type": "customer" if line.account_internal_type == "receivable" else "supplier",
            "payment_type": "inbound" if line.balance > 0.0 else "outbound",
        }

    def _get_batches(self):
        """Group the account.move.line linked to the wizard together.
        :return: A list of batches, each one containing:
            * key_values:   The key as a dictionary used to group the journal items together.
            * moves:        An account.move recordset.
        """
        self.ensure_one()

        lines = self.line_ids._origin

        if len(lines.company_id) > 1:
            raise UserError(_("You can't create payments for entries belonging to different companies."))
        if not lines:
            raise UserError(
                _("You can't open the register payment wizard without at least one receivable/payable line.")
            )

        batches = {}
        for line in lines:
            batch_key = self._get_line_batch_key(line)

            serialized_key = "-".join(str(v) for v in batch_key.values())
            batches.setdefault(
                serialized_key,
                {
                    "key_values": batch_key,
                    "lines": self.env["account.move.line"],
                },
            )
            batches[serialized_key]["lines"] += line
        return list(batches.values())

    @api.model
    def _get_wizard_values_from_batch(self, batch_result):
        """Extract values from the batch passed as parameter (see '_get_batches')
        to be mounted in the wizard view.
        :param batch_result:    A batch returned by '_get_batches'.
        :return:                A dictionary containing valid fields
        """
        key_values = batch_result["key_values"]
        lines = batch_result["lines"]
        company = lines[0].company_id

        source_amount = abs(sum(lines.mapped("amount_residual")))
        if key_values["currency_id"] == company.currency_id.id:
            source_amount_currency = source_amount
        else:
            source_amount_currency = abs(sum(lines.mapped("amount_residual_currency")))

        return {
            "company_id": company.id,
            "partner_id": key_values["partner_id"],
            "partner_type": key_values["partner_type"],
            "payment_type": key_values["payment_type"],
            "source_currency_id": key_values["currency_id"],
            "source_amount": source_amount,
            "source_amount_currency": source_amount_currency,
        }

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends("line_ids")
    def _compute_from_lines(self):
        """Load initial values from the account.moves passed through the context."""
        for wizard in self:
            batches = wizard._get_batches()
            batch_result = batches[0]
            wizard_values_from_batch = wizard._get_wizard_values_from_batch(batch_result)

            if len(batches) == 1:
                # == Single batch to be mounted on the view ==
                wizard.update(wizard_values_from_batch)

                wizard.can_edit_wizard = True
                wizard.can_group_payments = len(batch_result["lines"]) != 1
            else:
                # == Multiple batches: The wizard is not editable  ==
                wizard.update(
                    {
                        "company_id": batches[0]["lines"][0].company_id.id,
                        "partner_id": False,
                        "partner_type": False,
                        "payment_type": wizard_values_from_batch["payment_type"],
                        "source_currency_id": False,
                        "source_amount": False,
                        "source_amount_currency": False,
                    }
                )

                wizard.can_edit_wizard = False
                wizard.can_group_payments = any(len(batch_result["lines"]) != 1 for batch_result in batches)

    @api.depends("can_edit_wizard")
    def _compute_communication(self):
        # The communication can't be computed in '_compute_from_lines' because
        # it's a compute editable field and then, should be computed in a separated method.
        for wizard in self:
            if wizard.can_edit_wizard:
                batches = self._get_batches()
                wizard.communication = wizard._get_batch_communication(batches[0])
            else:
                wizard.communication = False

    @api.depends("can_edit_wizard")
    def _compute_group_payment(self):
        for wizard in self:
            if wizard.can_edit_wizard:
                batches = wizard._get_batches()
                wizard.group_payment = len(batches[0]["lines"].move_id) == 1
            else:
                wizard.group_payment = False

    @api.depends("company_id", "source_currency_id")
    def _compute_journal_id(self):
        for wizard in self:
            domain = [
                ("type", "in", ("bank", "cash")),
                ("company_id", "=", wizard.company_id.id),
            ]
            journal = None
            if wizard.source_currency_id:
                journal = self.env["account.journal"].search(
                    domain + [("currency_id", "=", wizard.source_currency_id.id)],
                    limit=1,
                )
            if not journal:
                journal = self.env["account.journal"].search(domain, limit=1)
            wizard.journal_id = journal

    @api.depends("journal_id")
    def _compute_currency_id(self):
        for wizard in self:
            wizard.currency_id = (
                wizard.journal_id.currency_id or wizard.source_currency_id or wizard.company_id.currency_id
            )

    @api.depends("partner_id")
    def _compute_partner_bank_id(self):
        """The default partner_bank_id will be the first available on the partner."""
        for wizard in self:
            available_partner_bank_accounts = wizard.partner_id.bank_ids.filtered(
                lambda x: x.company_id in (False, wizard.company_id)
            )
            if available_partner_bank_accounts:
                wizard.partner_bank_id = available_partner_bank_accounts[0]._origin
            else:
                wizard.partner_bank_id = False

    @api.depends(
        "payment_type",
        "journal_id.inbound_payment_method_ids",
        "journal_id.outbound_payment_method_ids",
    )
    def _compute_payment_method_fields(self):
        for wizard in self:
            if wizard.payment_type == "inbound":
                wizard.available_payment_method_ids = wizard.journal_id.inbound_payment_method_ids
            else:
                wizard.available_payment_method_ids = wizard.journal_id.outbound_payment_method_ids

            wizard.hide_payment_method = (
                len(wizard.available_payment_method_ids) == 1 and wizard.available_payment_method_ids.code == "manual"
            )

    @api.depends(
        "payment_type",
        "journal_id.inbound_payment_method_ids",
        "journal_id.outbound_payment_method_ids",
    )
    def _compute_payment_method_id(self):
        for wizard in self:
            if wizard.payment_type == "inbound":
                available_payment_methods = wizard.journal_id.inbound_payment_method_ids
            else:
                available_payment_methods = wizard.journal_id.outbound_payment_method_ids

            # Select the first available one by default.
            if available_payment_methods:
                wizard.payment_method_id = available_payment_methods[0]._origin
            else:
                wizard.payment_method_id = False

    @api.depends("payment_method_id")
    def _compute_show_require_partner_bank(self):
        """Computes if the destination bank account must be displayed in the payment form view. By default, it
        won't be displayed but some modules might change that, depending on the payment type."""
        for wizard in self:
            wizard.show_partner_bank_account = (
                wizard.payment_method_id.code in self.env["account.payment"]._get_method_codes_using_bank_account()
            )
            wizard.require_partner_bank_account = (
                wizard.payment_method_id.code in self.env["account.payment"]._get_method_codes_needing_bank_account()
            )

    @api.depends(
        "source_amount",
        "source_amount_currency",
        "source_currency_id",
        "company_id",
        "currency_id",
        "payment_date",
    )
    def _compute_amount(self):
        for wizard in self:
            if wizard.source_currency_id == wizard.currency_id:
                # Same currency.
                wizard.amount = wizard.source_amount_currency
            elif wizard.currency_id == wizard.company_id.currency_id:
                # Payment expressed on the company's currency.
                wizard.amount = wizard.source_amount
            else:
                # Foreign currency on payment different than the one set on the journal entries.
                amount_payment_currency = wizard.company_id.currency_id._convert(
                    wizard.source_amount,
                    wizard.currency_id,
                    wizard.company_id,
                    wizard.payment_date,
                )
                wizard.amount = amount_payment_currency

    @api.depends("register_line_ids.amount_writeoff", "amount")
    def _compute_payment_difference(self):
        for wizard in self:
            if wizard.source_currency_id == wizard.currency_id:
                # Same currency.
                writeoff_amount = sum(wizard.register_line_ids.mapped("amount_writeoff"))
                wizard.payment_difference = writeoff_amount
                wizard.payment_difference_handling = "reconcile" if writeoff_amount > 0 else False
            elif wizard.currency_id == wizard.company_id.currency_id:
                # Payment expressed on the company's currency.
                writeoff_amount = sum(wizard.register_line_ids.mapped("amount_writeoff"))
                wizard.payment_difference = writeoff_amount
                wizard.payment_difference_handling = "reconcile" if writeoff_amount > 0 else False
            else:
                # TODO: add cross currency payment support
                # Foreign currency on payment different than the one set on the journal entries.
                # amount_payment_currency = wizard.company_id.currency_id._convert(
                #     wizard.source_amount, wizard.currency_id, wizard.company_id, wizard.payment_date)
                wizard.payment_difference = 0
                wizard.payment_difference_handling = "open"

    # -------------------------------------------------------------------------
    # LOW-LEVEL METHODS
    # -------------------------------------------------------------------------

    @api.model
    def default_get(self, fields_list):
        # OVERRIDE
        res = super().default_get(fields_list)

        if "line_ids" in fields_list and "line_ids" not in res:

            # Retrieve moves to pay from the context.

            if self._context.get("active_model") == "account.move":
                lines = self.env["account.move"].browse(self._context.get("active_ids", [])).line_ids
            else:
                raise UserError(_("The register payment wizard should only be called on account.move records."))

            # Keep lines having a residual amount to pay.
            available_lines = self.env["account.move.line"]
            for line in lines:
                if line.move_id.state != "posted":
                    raise UserError(_("You can only register payment for posted journal entries."))

                if line.account_internal_type not in ("receivable", "payable"):
                    continue
                if line.currency_id:
                    if line.currency_id.is_zero(line.amount_residual_currency):
                        continue
                else:
                    if line.company_currency_id.is_zero(line.amount_residual):
                        continue
                available_lines |= line

            # Check.
            if not available_lines:
                raise UserError(
                    _(
                        "You can't register a payment because there is nothing left to "
                        "pay on the selected journal items."
                    )
                )
            if len(lines.company_id) > 1:
                raise UserError(_("You can't create payments for entries belonging to different companies."))
            if len(set(available_lines.mapped("account_internal_type"))) > 1:
                raise UserError(
                    _("You can't register payments for journal items being either all inbound, either all outbound.")
                )
            res["line_ids"] = [(6, 0, available_lines.ids)]

            # Used as flag for Bassam Customization
            res["is_initial"] = True

        # This is a dirty hack(?) done for the time being to find the type of account.move,
        # whether it's out_invoice, out_refund, in_invoice, in_refund.
        # TODO: Find a better solution
        res["move_type"] = self.env["account.move"].browse(self._context.get("active_ids", [])[0]).move_type

        return res

    # -------------------------------------------------------------------------
    # BUSINESS METHODS
    # -------------------------------------------------------------------------

    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            "date": self.payment_date,
            "amount": self.amount,
            "payment_type": self.payment_type,
            "partner_type": self.partner_type,
            "ref": self.communication,
            "journal_id": self.journal_id.id,
            "currency_id": self.currency_id.id,
            "partner_id": self.partner_id.id,
            "partner_bank_id": self.partner_bank_id.id,
            "payment_method_id": self.payment_method_id.id,
            "destination_account_id": self.line_ids[0].account_id.id,
        }

        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == "reconcile":
            payment_vals["write_off_line_vals"] = {
                "name": self.writeoff_label,
                "amount": self.payment_difference,
                "account_id": self.writeoff_account_id.id,
            }
        return payment_vals

    def _create_payment_vals_from_batch(self, batch_result):
        batch_values = self._get_wizard_values_from_batch(batch_result)
        register_line_id = self.register_line_ids.filtered(lambda x: x.move_id == batch_result["lines"].move_id)
        payment_vals = {
            "date": self.payment_date,
            "amount": register_line_id.amount_payment,
            "payment_type": batch_values["payment_type"],
            "partner_type": batch_values["partner_type"],
            "ref": self._get_batch_communication(batch_result),
            "journal_id": self.journal_id.id,
            "currency_id": batch_values["source_currency_id"],
            "partner_id": batch_values["partner_id"],
            "partner_bank_id": batch_result["key_values"]["partner_bank_id"],
            "payment_method_id": self.payment_method_id.id,
            "destination_account_id": batch_result["lines"][0].account_id.id,
        }

        if not register_line_id.currency_id.is_zero(register_line_id.amount_writeoff):
            payment_vals["write_off_line_vals"] = {
                "name": register_line_id.writeoff_label,
                "amount": register_line_id.amount_writeoff,
                "account_id": register_line_id.writeoff_account_id.id,
            }
        return payment_vals

    def _create_payments(self):
        self.ensure_one()
        batches = self._get_batches()
        edit_mode = self.can_edit_wizard and (len(batches[0]["lines"]) == 1 or self.group_payment)

        to_reconcile = []
        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard()
            payment_vals_list = [payment_vals]
            to_reconcile.append(batches[0]["lines"])
        else:
            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result["lines"]:
                        new_batches.append(
                            {
                                **batch_result,
                                "lines": line,
                            }
                        )
                batches = new_batches

            payment_vals_list = []
            for batch_result in batches:
                payment_vals_list.append(self._create_payment_vals_from_batch(batch_result))
                to_reconcile.append(batch_result["lines"])

        payments = self.env["account.payment"].create(payment_vals_list)

        # If payments are made using a currency different than the source one, ensure the balance match exactly in
        # order to fully paid the source journal items.
        # For example, suppose a new currency B having a rate 100:1 regarding the company currency A.
        # If you try to pay 12.15A using 0.12B, the computed balance will be 12.00A for the payment instead of 12.15A.
        if edit_mode:
            for payment, lines in zip(payments, to_reconcile):
                # Batches are made using the same currency so making 'lines.currency_id' is ok.
                if payment.currency_id != lines.currency_id:
                    (
                        liquidity_lines,
                        counterpart_lines,
                        writeoff_lines,
                    ) = payment._seek_for_lines()
                    source_balance = abs(sum(lines.mapped("amount_residual")))
                    payment_rate = liquidity_lines[0].amount_currency / liquidity_lines[0].balance
                    source_balance_converted = abs(source_balance) * payment_rate

                    # Translate the balance into the payment currency is order to be able to compare them.
                    # In case in both have the same value (12.15 * 0.01 ~= 0.12 in our example), it means the user
                    # attempt to fully paid the source lines and then, we need to manually fix them to get a perfect
                    # match.
                    payment_balance = abs(sum(counterpart_lines.mapped("balance")))
                    payment_amount_currency = abs(sum(counterpart_lines.mapped("amount_currency")))
                    if not payment.currency_id.is_zero(source_balance_converted - payment_amount_currency):
                        continue

                    delta_balance = source_balance - payment_balance

                    # Balance are already the same.
                    if self.company_currency_id.is_zero(delta_balance):
                        continue

                    # Fix the balance but make sure to peek the liquidity and counterpart lines first.
                    debit_lines = (liquidity_lines + counterpart_lines).filtered("debit")
                    credit_lines = (liquidity_lines + counterpart_lines).filtered("credit")

                    payment.move_id.write(
                        {
                            "line_ids": [
                                (
                                    1,
                                    debit_lines[0].id,
                                    {"debit": debit_lines[0].debit + delta_balance},
                                ),
                                (
                                    1,
                                    credit_lines[0].id,
                                    {"credit": credit_lines[0].credit + delta_balance},
                                ),
                            ]
                        }
                    )

        payments.action_post()

        domain = [
            ("account_internal_type", "in", ("receivable", "payable")),
            ("reconciled", "=", False),
        ]
        for payment, lines in zip(payments, to_reconcile):

            # When using the payment tokens, the payment could not be posted at this point (e.g. the transaction failed)
            # and then, we can't perform the reconciliation.
            if payment.state != "posted":
                continue

            payment_lines = payment.line_ids.filtered_domain(domain)
            payments_to_do = {}
            writeoff_to_do = {}
            move_ids = lines.mapped("move_id")
            # Find the payment amount and writeoff amount move wise
            for each_move in move_ids:
                register_line_id = self.register_line_ids.filtered(lambda x: x.move_id == each_move)
                payments_to_do[each_move] = register_line_id.amount_payment
                writeoff_to_do[each_move] = register_line_id.amount_writeoff
            for account in payment_lines.account_id:
                (payment_lines + lines).filtered_domain(
                    [("account_id", "=", account.id), ("reconciled", "=", False)]
                ).multi_reconcile(payments_to_do, writeoff_to_do, self.payment_date, self.move_type)

        return payments

    def action_create_payments(self):

        # Start Checks
        if self.amount_total <= 0 and self.group_payment:
            raise UserError(_("The payment amount should be positive!"))

        if self.amount != sum(self.register_line_ids.mapped("amount_payment")):
            raise ValidationError(_("The payment amount must be equal to the sum of the payment lines."))

        move_types = self.register_line_ids.move_id.mapped("move_type")
        if len(set(move_types)) > 1:
            raise UserError(_("You can only register payment against a single move type at a time!"))
        elif len(move_types) == 1 and self.move_type != move_types[0]:
            raise UserError(_("Incorrect move type found! Please register payments from respective forms!"))
        elif len(move_types) == 0:
            raise UserError(_("Please select at-least one move to register payment!"))

        # TODO: add cross currency payment support
        move_currencies = self.register_line_ids.move_id.mapped("currency_id")
        if len(move_currencies) > 1:
            raise UserError(_("Please select moves with the same currency!"))
        else:
            if move_currencies != self.currency_id:
                raise UserError(_("Please make payment in the same currency as of the move!"))
        # End Checks

        payments = self._create_payments()

        if self._context.get("dont_redirect_to_payments"):
            return True

        action = {
            "name": _("Payments"),
            "type": "ir.actions.act_window",
            "res_model": "account.payment",
            "context": {"create": False},
        }
        if len(payments) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": payments.id,
                }
            )
        else:
            action.update(
                {
                    "view_mode": "tree,form",
                    "domain": [("id", "in", payments.ids)],
                }
            )
        return action


class AccountMultiPaymentRegisterLine(models.TransientModel):
    _name = "account.multi.payment.register.line"
    _description = "Account Multi Payment Register Line"
    """
    Used to store the payment amount details entered by the user move_id wise
    """

    account_multi_payment_register_id = fields.Many2one(
        "account.multi.payment.register", store=True, string="Payment Register"
    )
    move_id = fields.Many2one("account.move", string="Invoice/Bill", required=True, store=True)
    company_currency_id = fields.Many2one(
        related="account_multi_payment_register_id.company_currency_id",
        string="Company Currency",
        readonly=True,
        store=True,
        help="Utility field to express company amount currency",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        store=True,
        readonly=False,
        compute="_compute_currency_id",
        help="The payment's currency.",
    )
    amount_total = fields.Monetary(
        string="Amount Total",
        store=True,
        compute="_compute_amount_total_residual",
        currency_field="company_currency_id",
    )
    amount_residual = fields.Monetary(
        string="Amount Due",
        store=True,
        compute="_compute_amount_total_residual",
        currency_field="company_currency_id",
    )
    amount_payment = fields.Monetary(string="Payment Amount", store=True, currency_field="currency_id")
    amount_writeoff = fields.Monetary(string="Write-Off Amount", store=True, currency_field="currency_id")
    partner_id = fields.Many2one("res.partner", string="Partner", related="move_id.partner_id", store=True)
    company_id = fields.Many2one(
        "res.company", store=True, copy=False, related="account_multi_payment_register_id.company_id"
    )
    writeoff_account_id = fields.Many2one(
        "account.account",
        string="Difference Account",
        copy=False,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
    )
    writeoff_label = fields.Char(
        string="Journal Item Label",
        default="Write-Off",
        help="Change label of the counterpart that will hold the payment difference",
    )

    @api.constrains("amount_writeoff", "amount_payment")
    def _check_total_writeoff_payment(self):
        for record in self:
            if (record.amount_writeoff + record.amount_payment) > record.amount_residual:
                raise ValidationError(
                    _(
                        "The sum of the write-off amount and the payment amount must be "
                        "less than or equal to the amount due."
                    )
                )

    @api.depends("account_multi_payment_register_id.journal_id")
    def _compute_currency_id(self):
        for record in self:
            record.currency_id = (
                record.account_multi_payment_register_id.journal_id.currency_id
                or record.account_multi_payment_register_id.source_currency_id
                or record.company_id.currency_id
            )

    @api.depends("move_id")
    def _compute_amount_total_residual(self):
        for record in self:
            if record.move_id:
                record.write(
                    {
                        "amount_total": record.move_id.amount_total,
                        "amount_residual": record.move_id.amount_residual,
                    }
                )
            else:
                record.write({"amount_total": 0.0, "amount_residual": 0.0})
