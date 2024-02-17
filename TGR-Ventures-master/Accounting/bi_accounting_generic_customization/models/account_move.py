from odoo.exceptions import UserError
from odoo import models, fields, api, _
from collections import defaultdict
from datetime import datetime


class AccountsMoveGeneric(models.Model):
    _inherit = "account.move"

    code_vendor = fields.Char(related="partner_id.vendor_code")
    code_customer = fields.Char(related="partner_id.customer_code")
    is_invoice_mail_send = fields.Boolean(string="Email Send", copy=False)
    warehouse_id = fields.Many2one(
        string="Warehouse",
        comodel_name="stock.warehouse",
        ondelete="restrict",
        compute="_compute_picking_details",
        store=True,
    )
    picking_id = fields.Many2one(
        string="Picking",
        comodel_name="stock.picking",
        ondelete="restrict",
        compute="_compute_picking_details",
        store=True,
    )
    picking_date = fields.Datetime(string="Picking Date", compute="_compute_picking_date", store=True)
    partner_country_id = fields.Many2one(
        string="Country",
        comodel_name="res.country",
        ondelete="restrict",
        compute="_compute_partner_country",
        store=True,
    )
    is_accumilative_invoice = fields.Boolean("Is Accumilative Invoice")
    initial_series = fields.Char("Initial Series")
    final_series = fields.Char("Final Series")
    is_service_bill = fields.Boolean("Is Service Bill")
    edi_mark_as_sent = fields.Boolean("Mark As Sent", copy=False)
    original_invoice_id = fields.Many2one("account.move", string="Original Invoice")
    original_bill_id = fields.Many2one("account.move", string="Original Bill")
    original_invoice_date = fields.Date("Original Invoice Date")
    original_invoice_untaxed_amount = fields.Monetary("Original Invoice Taxable Amount")
    edi_banner_hide = fields.Boolean("Edi Banner Hide")
    partner_vat = fields.Char(string="Vat Number", related="partner_id.vat")
    is_uk = fields.Boolean("Is UK", related="warehouse_id.is_uk")
    is_spain = fields.Boolean("Is Spain", related="warehouse_id.is_spain")
    analytic_account_id = fields.Many2one("account.analytic.account", string="Analytic Account")
    analytic_tag_ids = fields.Many2many("account.analytic.tag", string="Analytic Tags")
    receipt_date = fields.Datetime("Receipt Date")
    partner_state_id = fields.Many2one('res.country.state', related='partner_id.state_id', string="Partner State")

    @api.depends("edi_document_ids.state", "edi_mark_as_sent")
    def _compute_edi_state(self):
        for move in self:
            if move.edi_mark_as_sent:
                for move_doc in move.edi_document_ids.filtered(lambda d: d.edi_format_id._needs_web_services()):
                    move_doc.state = "sent"
            # else:
            #     for move_doc in move.edi_document_ids.filtered(lambda d: d.edi_format_id._needs_web_services()):
            #         move_doc.state = 'to_send'
            all_states = set(
                move.edi_document_ids.filtered(lambda d: d.edi_format_id._needs_web_services()).mapped("state")
            )
            if all_states == {"sent"}:
                move.edi_state = "sent"
            elif all_states == {"cancelled"}:
                move.edi_state = "cancelled"
            elif "to_send" in all_states:
                move.edi_state = "to_send"
            elif "to_cancel" in all_states:
                move.edi_state = "to_cancel"
            else:
                move.edi_state = False

    @api.model
    def create(self, vals):
        if vals.get("move_type") in ["out_refund", "in_refund"] and vals.get("reversed_entry_id"):
            reverse_move = self.env["account.move"].browse(vals.get("reversed_entry_id"))
            vals.update(
                {
                    "original_invoice_date": reverse_move.invoice_date,
                    "original_invoice_untaxed_amount": reverse_move.amount_untaxed,
                }
            )
            if vals.get("move_type") == "out_refund":
                vals["original_invoice_id"] = reverse_move.id
            elif vals.get("move_type") == "in_refund":
                vals["original_bill_id"] = reverse_move.id

        res = super(AccountsMoveGeneric, self).create(vals)
        for move in res:
            move._onchange_partner_id()
        return res

    @api.onchange("original_invoice_id")
    def _onchange_original_invoice_id(self):
        for rec in self:
            if rec.original_invoice_id:
                rec.original_invoice_date = rec.original_invoice_id.invoice_date
                rec.original_invoice_untaxed_amount = rec.original_invoice_id.amount_untaxed

    @api.onchange("original_bill_id")
    def _onchange_original_invoice_id(self):
        for rec in self:
            if rec.original_bill_id:
                rec.original_invoice_date = rec.original_bill_id.invoice_date
                rec.original_invoice_untaxed_amount = rec.original_bill_id.amount_untaxed

    def l10n_es_reports_mod349_available_cron(self):
        eu_country_codes = set(self.env.ref("base.europe").country_ids.mapped("code"))
        # Mod 349 is required for all EU operations with companies, except Spain
        # mod349_countries = self.env.ref('base.europe').country_ids.filtered_domain([('code', '!=', 'ES')])
        invoices = self.env["account.move"].search([("move_type", "in", ["out_invoice"])])
        for invoice in invoices:
            if invoice.partner_id.country_id.code in eu_country_codes and invoice.partner_id.country_id.code != "ES":
                tax_ids = invoice.invoice_line_ids[0].mapped("tax_ids").ids
                if 103 in tax_ids:
                    invoice.l10n_es_reports_mod349_available = True
                else:
                    invoice.l10n_es_reports_mod349_available = False
            else:
                invoice.l10n_es_reports_mod349_available = False

    def l10n_es_reports_mod349_credit_note_available_cron(self):
        eu_country_codes = set(self.env.ref("base.europe").country_ids.mapped("code"))
        # Mod 349 is required for all EU operations with companies, except Spain
        # mod349_countries = self.env.ref('base.europe').country_ids.filtered_domain([('code', '!=', 'ES')])
        invoices = self.env["account.move"].search([("move_type", "in", ["out_refund"])])
        for invoice in invoices:
            if invoice.partner_id.country_id.code in eu_country_codes and invoice.partner_id.country_id.code != "ES":
                if invoice.invoice_line_ids:
                    tax_ids = invoice.invoice_line_ids[0].mapped("tax_ids").ids
                    if 103 in tax_ids:
                        invoice.l10n_es_reports_mod349_available = True
                    else:
                        invoice.l10n_es_reports_mod349_available = False
            else:
                invoice.l10n_es_reports_mod349_available = False

    @api.depends("partner_id.country_id", "invoice_line_ids.tax_ids")
    def _compute_l10n_es_reports_mod349_available(self):
        set(self.env.ref("base.europe").country_ids.mapped("code"))
        # # Mod 349 is required for all EU operations with companies, except Spain
        # mod349_countries = self.env.ref('base.europe').country_ids.filtered_domain([('code', '!=', 'ES')])
        for invoice in self:
            if invoice.move_type in ["out_invoice", "out_refund"]:
                if invoice.invoice_line_ids:
                    tax_ids = invoice.invoice_line_ids[0].mapped("tax_ids").ids
                    if any(tax in [52, 103] for tax in tax_ids):
                        invoice.l10n_es_reports_mod349_available = True
                    else:
                        invoice.l10n_es_reports_mod349_available = False
                else:
                    invoice.l10n_es_reports_mod349_available = False
            elif invoice.move_type in ["in_invoice", "in_refund"]:
                if invoice.invoice_line_ids:
                    tax_ids = invoice.invoice_line_ids[0].mapped("tax_ids").ids
                    if any(tax in [39, 40, 41, 48, 49, 50, 51, 116, 117, 242] for tax in tax_ids):
                        invoice.l10n_es_reports_mod349_available = True
                    else:
                        invoice.l10n_es_reports_mod349_available = False
                else:
                    invoice.l10n_es_reports_mod349_available = False
            else:
                invoice.l10n_es_reports_mod349_available = False

    def action_mod349_available(self):
        for rec in self:
            rec._compute_l10n_es_reports_mod349_available()

    @api.depends("partner_id", "partner_shipping_id", "partner_shipping_id.country_id")
    def _compute_partner_country(self):
        for invoice in self:
            if invoice.partner_shipping_id:
                invoice.partner_country_id = invoice.partner_shipping_id.country_id.id
            else:
                invoice.partner_country_id = False

    @api.depends("picking_id.date_done")
    def _compute_picking_date(self):
        for invoice in self:
            if invoice.picking_id:
                invoice.picking_date = invoice.picking_id.date_done
            else:
                invoice.picking_date = False

    @api.depends("invoice_line_ids")
    def _compute_picking_details(self):
        for invoice in self:
            sale_id = self.env["sale.order"].search([("invoice_ids", "in", invoice.ids)], limit=1)
            if sale_id and sale_id.warehouse_id:
                invoice.warehouse_id = sale_id.warehouse_id.id
            else:
                invoice.warehouse_id = False
            invoice.picking_id = False
            if sale_id and sale_id.picking_ids:
                if sale_id.picking_ids.filtered(lambda pick: pick.state != "cancel"):
                    invoice.picking_id = sale_id.picking_ids.filtered(lambda pick: pick.state != "cancel")[0].id
            else:
                invoice.picking_id = False

    def _post_invoice_based_on_picking(self):
        for invoice in self:
            if (
                invoice.picking_id
                and invoice.picking_id.date_done
                and invoice.picking_id.state == "done"
                and invoice.state == "draft"
            ):
                invoice.invoice_date = invoice.picking_id.date_done
                invoice._onchange_invoice_date()
                invoice.action_post()

    @api.onchange("partner_id", "name")
    def _onchange_partner_id(self):
        res = super(AccountsMoveGeneric, self)._onchange_partner_id()
        for each in self.filtered(lambda amv: amv.move_type != "entry"):
            for line in each.invoice_line_ids.filtered(lambda inv_line: not inv_line.display_type):
                line.account_id = line._get_computed_account() or self.journal_id.default_account_id
                if 'is_ez_import' in self._context:
                    line.account_id = self._context['account_id']
                if (
                    each.is_sale_document(include_receipts=True)
                    and each.partner_id
                    and each.partner_id.sales_account_id
                ):
                    line.account_id = line.move_id.partner_id.sales_account_id.id
                elif (
                    each.is_purchase_document(include_receipts=True)
                    and each.partner_id
                    and each.partner_id.exp_account_id
                ):
                    line.account_id = line.move_id.partner_id.exp_account_id.id
            if each.move_type == "out_invoice" or each.move_type == "out_refund":
                return {"domain": {"partner_id": [("is_customer", "=", True)]}}
            elif each.move_type == "in_invoice" or each.move_type == "in_refund":
                return {"domain": {"partner_id": [("is_supplier", "=", True)]}}
        return res

    # def send_invoice_cron(self):
    #     records = self.env["account.move"].search(
    #         [
    #             ("state", "=", "posted"),
    #             ("move_type", "in", ("out_invoice", "out_refund")),
    #             ("is_invoice_mail_send", "=", False),
    #         ]
    #     )
    #     template = self.env.ref("account.email_template_edi_invoice")
    #     template.email_from = "info@tiger-one.eu"
    #     for record in records:
    #         if record.magento_website_id.id in (2, 1):
    #             template.send_mail(record.id, force_send=True)
    #             record.is_invoice_mail_send = True

    def action_post(self):
        result = super(AccountsMoveGeneric, self).action_post()
        for record in self:
            if record.move_type in ("out_invoice", "out_refund"):
                if record.magento_website_id.id in (2, 1) and not record.is_invoice_mail_send:
                    if record.move_type == "out_invoice":
                        template = self.env.ref("account.email_template_edi_invoice")
                    else:
                        template = self.env.ref("account.email_template_edi_credit_note")
                    template.email_from = "info@tiger-one.eu"
                    template.send_mail(record.id, force_send=True)
                    record.is_invoice_mail_send = True
        return result

    # def update_line_taxes(self, invoice_date=False):
    #     invoices = self.env["account.move"].search(
    #         [
    #             ("move_type", "in", ["out_invoice"]),
    #             ("state", "=", "draft"),
    #             ("warehouse_id", "=", 17),
    #             ("invoice_date", "=", datetime.strptime(invoice_date, "%d-%m-%Y").date()),
    #             ("picking_date", "!=", False),
    #         ]
    #     )
    #     for invoice in invoices:
    #         country = invoice.partner_id.country_id
    #         set(self.env.ref("base.europe").country_ids.mapped("code"))
    #         invoice.partner_country_id
    #         if country and country.code == "ES":
    #             required_tax = self.env["account.tax"].browse(34)  # IVA 21% (Bienes)
    #             for line in invoice.invoice_line_ids:
    #                 if line.tax_ids:
    #                     line.update({"tax_ids": [(3, tax.id) for tax in line.tax_ids]})
    #                 line.update({"tax_ids": [(4, required_tax.id)]})
    #         invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)

    # FUNCTION IS USED TO RUN SCHEDUKER TO CHANGE WAREHOUSE
    def change_warehouse(self):
        uk_list = ["INV/2023/01990", "INV/2023/03803"]
        malaga_list = [
            "INV/2023/06065",
            "INV/2023/06676",
            "INV/2023/03788",
            "INV/2023/06137",
            "INV/2023/00362",
            "INV/2023/00059",
            "INV/2023/00056",
            "INV/2023/00030",
            "INV/2022/00076",
            "INV/2022/00080",
            "INV/2023/04878",
            "INV/2023/04879",
            "INV/2023/00055",
            "INV/2022/00074",
        ]
        for uk in uk_list:
            uk_warehouse_id = self.env["stock.warehouse"].search([("id", "=", 15)])
            invoice_id = self.env["account.move"].search([("name", "=", uk)], limit=1)
            if invoice_id:
                invoice_id.warehouse_id = uk_warehouse_id.id
        for malaga in malaga_list:
            malaga_warehouse_id = self.env["stock.warehouse"].search([("id", "=", 17)])
            invoice_id = self.env["account.move"].search([("name", "=", malaga)], limit=1)
            if invoice_id:
                invoice_id.warehouse_id = malaga_warehouse_id.id

    # CHANGE TAX FOR UK WAREHOUSE
    def update_uk_line_taxes(self, invoice_start_date=False, invoice_end_date=False):
        invoices = self.env["account.move"].search(
            [
                ("move_type", "in", ["out_invoice"]),
                ("state", "=", "draft"),
                ("warehouse_id", "=", 15),
                ("invoice_date", ">=", datetime.strptime(invoice_start_date, "%d-%m-%Y").date()),
                ("invoice_date", "<=", datetime.strptime(invoice_end_date, "%d-%m-%Y").date()),
                ("amount_tax", "=", 0),
            ]
        )
        for invoice in invoices:
            if invoice.picking_date and invoice.amount_tax == 0:
                invoice.partner_id.country_id
                eu_country_codes = set(self.env.ref("base.europe").country_ids.mapped("code"))
                delivery_country = invoice.partner_country_id
                # if delivery_country and delivery_country.code == 'GB':
                if delivery_country and delivery_country.code not in eu_country_codes:
                    required_tax = self.env["account.tax"].browse(5380)  # GB VAT 0%
                    for line in invoice.invoice_line_ids:
                        if line.tax_ids:
                            line.update({"tax_ids": [(3, tax.id) for tax in line.tax_ids]})
                        line.update({"tax_ids": [(4, required_tax.id)]})
                invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)

    # CHANGE TAX FOR UK3PL WAREHOUSE
    def update_uk3pl_line_taxes(self, invoice_start_date=False, invoice_end_date=False):
        invoices = self.env["account.move"].search(
            [
                ("move_type", "in", ["out_invoice"]),
                ("state", "=", "draft"),
                ("warehouse_id", "=", 16),
                ("invoice_date", ">=", datetime.strptime(invoice_start_date, "%d-%m-%Y").date()),
                ("invoice_date", "<=", datetime.strptime(invoice_end_date, "%d-%m-%Y").date()),
                ("amount_tax", "=", 0),
            ]
        )
        for invoice in invoices:
            if invoice.picking_date and invoice.amount_tax == 0:
                invoice.partner_id.country_id
                eu_country_codes = set(self.env.ref("base.europe").country_ids.mapped("code"))
                delivery_country = invoice.partner_country_id
                # if delivery_country and delivery_country.code == 'GB':
                if delivery_country and delivery_country.code not in eu_country_codes:
                    required_tax = self.env["account.tax"].browse(5380)  # GB VAT 0%
                    for line in invoice.invoice_line_ids:
                        if line.tax_ids:
                            line.update({"tax_ids": [(3, tax.id) for tax in line.tax_ids]})
                        line.update({"tax_ids": [(4, required_tax.id)]})
                invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)

    def update_line_taxes_eu_not_es(self, invoice_date=False):
        invoices = self.env["account.move"].search(
            [
                ("move_type", "in", ["out_invoice"]),
                ("state", "=", "draft"),
                ("warehouse_id", "=", 17),
                ("invoice_date", "=", datetime.strptime(invoice_date, "%d-%m-%Y").date()),
                ("picking_date", "!=", False),
            ],
            limit=10,
        )
        for invoice in invoices:
            country = invoice.partner_id.country_id
            eu_country_codes = set(self.env.ref("base.europe").country_ids.mapped("code"))
            invoice.partner_country_id
            if country and country.code != "ES" and country.code in eu_country_codes and bool(invoice.partner_id.vat):
                required_tax = self.env["account.tax"].browse(103)  # IVA 0% Entregas Intracomunitarias exentas
                for line in invoice.invoice_line_ids:
                    if line.tax_ids:
                        line.with_context(check_move_validity=False).update(
                            {"tax_ids": [(3, tax.id) for tax in line.tax_ids]}
                        )
                    line.with_context(check_move_validity=False).update({"tax_ids": [(4, required_tax.id)]})
                invoice.fiscal_position_id = 3
            invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)

    def update_line_taxes_oss(self, invoice_date=False):
        invoices = self.env["account.move"].search(
            [
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("state", "=", "draft"),
                ("invoice_date", "=", datetime.strptime(invoice_date, "%d-%m-%Y").date()),
                ("picking_date", "!=", False),
            ]
        )
        for invoice in invoices:
            country = invoice.partner_id.country_id
            eu_country_codes = set(self.env.ref("base.europe").country_ids.mapped("code"))
            fiscal_position = self.env["account.fiscal.position"].search([("country_id", "=", country.id)], limit=1)
            if (
                country
                and country.code != "ES"
                and country.code in eu_country_codes
                and not bool(invoice.partner_id.vat)
            ):
                avail_fisc_taxes = fiscal_position.tax_ids.mapped("tax_src_id").filtered(
                    lambda fisc_tax: fisc_tax.type_tax_use == "sale" and fisc_tax.tax_scope == "consu"
                )
                required_fiscal_src_tax = avail_fisc_taxes.filtered(
                    lambda aft: aft.amount == max(avail_fisc_taxes.mapped("amount"))
                )
                required_fiscal_line = fiscal_position.tax_ids.filtered(
                    lambda fiscal_line: fiscal_line.tax_src_id == required_fiscal_src_tax
                )
                required_fiscal_dest_tax = required_fiscal_line.tax_dest_id
                for line in invoice.invoice_line_ids:
                    if line.tax_ids:
                        line.with_context(check_move_validity=False).update(
                            {"tax_ids": [(3, tax.id) for tax in line.tax_ids]}
                        )
                    line.with_context(check_move_validity=False).update({"tax_ids": [(4, required_fiscal_dest_tax.id)]})
            invoice.fiscal_position_id = fiscal_position.id
            invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)

    def update_line_taxes_for_delivery_to_spain(self):
        invoices = self.env["account.move"].search(
            [("move_type", "in", ["out_invoice", "out_refund"]), ("state", "=", "draft")]
        )
        for invoice in invoices.filtered(lambda inv: inv.partner_country_id.code == "ES"):
            invoice.partner_id.country_id
            set(self.env.ref("base.europe").country_ids.mapped("code"))
            delivery_country = invoice.partner_country_id
            if delivery_country and delivery_country.code == "ES":
                required_tax = self.env["account.tax"].browse(34)  # IVA 21% (Bienes)
                for line in invoice.invoice_line_ids:
                    if line.tax_ids:
                        line.update({"tax_ids": [(3, tax.id) for tax in line.tax_ids]})
                    line.update({"tax_ids": [(4, required_tax.id)]})

    # server-action function to cancel invoice
    # if corresponding picking is cancelled

    def cancel_invoice_by_picking(self):
        for move in self:
            if move.picking_id.state == "cancel":
                move.button_cancel()

    def _prepare_edi_tax_details(
        self, filter_to_apply=None, filter_invl_to_apply=None, grouping_key_generator=None, compute_mode="tax_details"
    ):
        """Compute amounts related to taxes for the current invoice.

        :param filter_to_apply:         Optional filter to exclude some tax values from the final results.
                                        The filter is defined as a method getting a dictionary as parameter
                                        representing the tax values for a single repartition line.
                                        This dictionary contains:

            'base_line_id':             An account.move.line record.
            'tax_id':                   An account.tax record.
            'tax_repartition_line_id':  An account.tax.repartition.line record.
            'base_amount':              The tax base amount expressed in company currency.
            'tax_amount':               The tax amount expressed in company currency.
            'base_amount_currency':     The tax base amount expressed in foreign currency.
            'tax_amount_currency':      The tax amount expressed in foreign currency.

                                        If the filter is returning False, it means the current tax values will be
                                        ignored when computing the final results.

        :param filter_invl_to_apply:    Optional filter to exclude some invoice lines.

        :param grouping_key_generator:  Optional method used to group tax values together. By default, the tax values
                                        are grouped by tax. This parameter is a method getting a dictionary as parameter
                                        (same signature as 'filter_to_apply').

                                        This method must returns a dictionary where values will be used to create the
                                        grouping_key to aggregate tax values together. The returned dictionary is added
                                        to each tax details in order to retrieve the full grouping_key later.

        :param compute_mode:            Optional parameter to specify the method used to allocate the tax line amounts
                                        among the invoice lines:
                                        'tax_details' (the default) uses the AccountMove._get_query_tax_details method.
                                        'compute_all' uses the AccountTax._compute_all method.

                                        The 'tax_details' method takes the tax line balance and allocates it among the
                                        invoice lines to which that tax applies, proportionately to the invoice lines'
                                        base amounts. This always ensures that the sum of the tax amounts equals the
                                        tax line's balance, which, depending on the constraints of a particular
                                        localization, can be more appropriate when 'Round Globally' is set.

                                        The 'compute_all' method returns, for each invoice line, the exact tax amounts
                                        corresponding to the taxes applied to the invoice line. Depending on the
                                        constraints of the particular localization, this can be more appropriate when
                                        'Round per Line' is set.

        :return:                        The full tax details for the current invoice and for each invoice line
                                        separately. The returned dictionary is the following:

            'base_amount':              The total tax base amount in company currency for the whole invoice.
            'tax_amount':               The total tax amount in company currency for the whole invoice.
            'base_amount_currency':     The total tax base amount in foreign currency for the whole invoice.
            'tax_amount_currency':      The total tax amount in foreign currency for the whole invoice.
            'tax_details':              A mapping of each grouping key (see 'grouping_key_generator') to a dictionary
                                        containing:

                'base_amount':              The tax base amount in company currency for the current group.
                'tax_amount':               The tax amount in company currency for the current group.
                'base_amount_currency':     The tax base amount in foreign currency for the current group.
                'tax_amount_currency':      The tax amount in foreign currency for the current group.
                'group_tax_details':        The list of all tax values aggregated into this group.

            'invoice_line_tax_details': A mapping of each invoice line to a dictionary containing:

                'base_amount':          The total tax base amount in company currency for the whole invoice line.
                'tax_amount':           The total tax amount in company currency for the whole invoice line.
                'base_amount_currency': The total tax base amount in foreign currency for the whole invoice line.
                'tax_amount_currency':  The total tax amount in foreign currency for the whole invoice line.
                'tax_details':          A mapping of each grouping key (see 'grouping_key_generator') to a dictionary
                                        containing:

                    'base_amount':          The tax base amount in company currency for the current group.
                    'tax_amount':           The tax amount in company currency for the current group.
                    'base_amount_currency': The tax base amount in foreign currency for the current group.
                    'tax_amount_currency':  The tax amount in foreign currency for the current group.
                    'group_tax_details':    The list of all tax values aggregated into this group.

        """
        self.ensure_one()

        def _serialize_python_dictionary(vals):
            return "-".join(str(vals[k]) for k in sorted(vals.keys()))

        def default_grouping_key_generator(tax_values):
            return {"tax": tax_values["tax_id"]}

        def compute_invoice_lines_tax_values_dict_from_tax_details(invoice_lines):
            invoice_lines_tax_values_dict = defaultdict(list)
            tax_details_query, tax_details_params = invoice_lines._get_query_tax_details_from_domain(
                [("move_id", "=", self.id)]
            )
            self._cr.execute(tax_details_query, tax_details_params)
            for row in self._cr.dictfetchall():
                invoice_line = invoice_lines.browse(row["base_line_id"])
                tax_line = invoice_lines.browse(row["tax_line_id"])
                src_line = invoice_lines.browse(row["src_line_id"])
                tax = self.env["account.tax"].browse(row["tax_id"])
                src_tax = self.env["account.tax"].browse(row["group_tax_id"]) if row["group_tax_id"] else tax

                invoice_lines_tax_values_dict[invoice_line].append(
                    {
                        "base_line_id": invoice_line,
                        "tax_line_id": tax_line,
                        "src_line_id": src_line,
                        "tax_id": tax,
                        "src_tax_id": src_tax,
                        "tax_repartition_line_id": tax_line.tax_repartition_line_id,
                        "base_amount": row["base_amount"],
                        "tax_amount": row["tax_amount"],
                        "base_amount_currency": row["base_amount_currency"],
                        "tax_amount_currency": row["tax_amount_currency"],
                    }
                )
            return invoice_lines_tax_values_dict

        def compute_invoice_lines_tax_values_dict_from_compute_all(invoice_lines):
            invoice_lines_tax_values_dict = {}
            sign = -1 if self.is_inbound() else 1
            for invoice_line in invoice_lines:
                taxes_res = invoice_line.tax_ids.compute_all(
                    invoice_line.price_unit * (1 - (invoice_line.discount / 100.0)),
                    currency=invoice_line.currency_id,
                    quantity=invoice_line.quantity,
                    product=invoice_line.product_id,
                    partner=invoice_line.partner_id,
                    is_refund=invoice_line.move_id.move_type in ("in_refund", "out_refund"),
                )
                invoice_lines_tax_values_dict[invoice_line] = []
                rate = (
                    abs(invoice_line.balance) / abs(invoice_line.amount_currency)
                    if invoice_line.amount_currency
                    else 0.0
                )
                for tax_res in taxes_res["taxes"]:
                    tax_amount = tax_res["amount"] * rate
                    if self.company_id.tax_calculation_rounding_method == "round_per_line":
                        tax_amount = invoice_line.company_currency_id.round(tax_amount)
                    invoice_lines_tax_values_dict[invoice_line].append(
                        {
                            "base_line_id": invoice_line,
                            "tax_id": self.env["account.tax"].browse(tax_res["id"]),
                            "tax_repartition_line_id": self.env["account.tax.repartition.line"].browse(
                                tax_res["tax_repartition_line_id"]
                            ),
                            "base_amount": sign * invoice_line.company_currency_id.round(tax_res["base"] * rate),
                            "tax_amount": sign * tax_amount,
                            "base_amount_currency": sign * tax_res["base"],
                            "tax_amount_currency": sign * tax_res["amount"],
                        }
                    )
            return invoice_lines_tax_values_dict

        # Compute the taxes values for each invoice line.
        invoice_lines = self.invoice_line_ids.filtered(lambda line: not line.display_type)
        if self.move_type == "in_invoice" and self.is_service_bill:
            invoice_lines = invoice_lines.filtered(lambda line: line.product_id.type == "service")
        if filter_invl_to_apply:
            invoice_lines = invoice_lines.filtered(filter_invl_to_apply)

        if compute_mode == "compute_all":
            invoice_lines_tax_values_dict = compute_invoice_lines_tax_values_dict_from_compute_all(invoice_lines)
        else:
            invoice_lines_tax_values_dict = compute_invoice_lines_tax_values_dict_from_tax_details(invoice_lines)

        grouping_key_generator = grouping_key_generator or default_grouping_key_generator

        # Apply 'filter_to_apply'.

        if self.move_type in ("out_refund", "in_refund"):
            tax_rep_lines_field = "refund_repartition_line_ids"
        else:
            tax_rep_lines_field = "invoice_repartition_line_ids"

        filtered_invoice_lines_tax_values_dict = {}
        for invoice_line in invoice_lines:
            tax_values_list = invoice_lines_tax_values_dict.get(invoice_line, [])
            filtered_invoice_lines_tax_values_dict[invoice_line] = []

            # Search for unhandled taxes.
            taxes_set = set(invoice_line.tax_ids.flatten_taxes_hierarchy())
            for tax_values in tax_values_list:
                taxes_set.discard(tax_values["tax_id"])

                if not filter_to_apply or filter_to_apply(tax_values):
                    filtered_invoice_lines_tax_values_dict[invoice_line].append(tax_values)

            # Restore zero-tax tax details.
            for zero_tax in taxes_set:

                affect_base_amount = 0.0
                affect_base_amount_currency = 0.0
                for tax_values in tax_values_list:
                    if zero_tax in tax_values["tax_line_id"].tax_ids:
                        affect_base_amount += tax_values["tax_amount"]
                        affect_base_amount_currency += tax_values["tax_amount_currency"]

                for tax_rep in zero_tax[tax_rep_lines_field].filtered(lambda x: x.repartition_type == "tax"):
                    tax_values = {
                        "base_line_id": invoice_line,
                        "tax_line_id": self.env["account.move.line"],
                        "src_line_id": invoice_line,
                        "tax_id": zero_tax,
                        "src_tax_id": zero_tax,
                        "tax_repartition_line_id": tax_rep,
                        "base_amount": invoice_line.balance + affect_base_amount,
                        "tax_amount": 0.0,
                        "base_amount_currency": invoice_line.amount_currency + affect_base_amount_currency,
                        "tax_amount_currency": 0.0,
                    }

                    if not filter_to_apply or filter_to_apply(tax_values):
                        filtered_invoice_lines_tax_values_dict[invoice_line].append(tax_values)

        # Initialize the results dict.

        invoice_global_tax_details = {
            "base_amount": 0.0,
            "tax_amount": 0.0,
            "base_amount_currency": 0.0,
            "tax_amount_currency": 0.0,
            "tax_details": defaultdict(
                lambda: {
                    "base_amount": 0.0,
                    "tax_amount": 0.0,
                    "base_amount_currency": 0.0,
                    "tax_amount_currency": 0.0,
                    "group_tax_details": [],
                }
            ),
            "invoice_line_tax_details": defaultdict(
                lambda: {
                    "base_amount": 0.0,
                    "tax_amount": 0.0,
                    "base_amount_currency": 0.0,
                    "tax_amount_currency": 0.0,
                    "tax_details": defaultdict(
                        lambda: {
                            "base_amount": 0.0,
                            "tax_amount": 0.0,
                            "base_amount_currency": 0.0,
                            "tax_amount_currency": 0.0,
                            "group_tax_details": [],
                        }
                    ),
                }
            ),
        }

        # Apply 'grouping_key_generator' to 'invoice_lines_tax_values_list' and add all values to the final results.

        for invoice_line in invoice_lines:
            tax_values_list = filtered_invoice_lines_tax_values_dict[invoice_line]

            key_by_tax = {}

            # Add to invoice global tax amounts.
            invoice_global_tax_details["base_amount"] += invoice_line.balance
            invoice_global_tax_details["base_amount_currency"] += invoice_line.amount_currency

            for tax_values in tax_values_list:
                grouping_key = grouping_key_generator(tax_values)
                serialized_grouping_key = _serialize_python_dictionary(grouping_key)
                key_by_tax[tax_values["tax_id"]] = serialized_grouping_key

                # Add to invoice line global tax amounts.
                if serialized_grouping_key not in invoice_global_tax_details["invoice_line_tax_details"][invoice_line]:
                    invoice_line_global_tax_details = invoice_global_tax_details["invoice_line_tax_details"][
                        invoice_line
                    ]
                    invoice_line_global_tax_details.update(
                        {
                            "base_amount": invoice_line.balance,
                            "base_amount_currency": invoice_line.amount_currency,
                        }
                    )
                else:
                    invoice_line_global_tax_details = invoice_global_tax_details["invoice_line_tax_details"][
                        invoice_line
                    ]

                self._add_edi_tax_values(
                    invoice_global_tax_details,
                    grouping_key,
                    serialized_grouping_key,
                    tax_values,
                    key_by_tax=key_by_tax if compute_mode == "tax_details" else None,
                )
                self._add_edi_tax_values(
                    invoice_line_global_tax_details,
                    grouping_key,
                    serialized_grouping_key,
                    tax_values,
                    key_by_tax=key_by_tax if compute_mode == "tax_details" else None,
                )

        return invoice_global_tax_details

    def _action_mark_as_sent(self):
        for line in self:
            line.write({"edi_mark_as_sent": True})

    def update_shipping_address_by_sale(self):
        for invoice in self:
            order = self.env["sale.order"].search([("invoice_ids", "=", invoice.ids)], limit=1)
            if order and order.partner_shipping_id:
                invoice.partner_shipping_id = order.partner_shipping_id

    @api.onchange("analytic_account_id", "analytic_tag_ids")
    def _onchange_account_analytic_line(self):
        for line in self.invoice_line_ids:
            line.analytic_account_id = False
            line.analytic_tag_ids = False
            if self.analytic_account_id:
                line.analytic_account_id = self.analytic_account_id.id
            if self.analytic_tag_ids:
                line.analytic_tag_ids = self.analytic_tag_ids

    def button_process_edi_web_services(self):
        for rec in self:
            tax_id = rec.invoice_line_ids[0] and rec.invoice_line_ids[0].tax_ids or []
            for tax in tax_id:
                if tax.is_uk_tax:
                    raise UserError(_("This record contain UK Tax"))
        return super().button_process_edi_web_services()

    @api.onchange("date")
    def _onchange_accounting_date(self):
        for rec in self:
            po = self.env["purchase.order"].search([("invoice_ids.id", "=", self._origin.id)], limit=1)
            if rec.move_type == "in_invoice" and po:
                if po.picking_ids:
                    effective_date = max(
                        po.picking_ids.filtered(lambda pick: pick.state == "done").mapped("date_done")
                    ).date()
                    if rec.date != effective_date:
                        return {
                            "warning": {
                                "title": "Alert Message",
                                "message": "Accounting date and Receipt date should be same",
                            },
                        }


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        for line in self.filtered(lambda inv_line: not inv_line.display_type):
            if (
                line.move_id.is_sale_document(include_receipts=True)
                and line.move_id.partner_id
                and line.move_id.partner_id.sales_account_id
            ):
                line.account_id = line.move_id.partner_id.sales_account_id.id
            elif (
                line.move_id.is_purchase_document(include_receipts=True)
                and line.move_id.partner_id
                and line.move_id.partner_id.exp_account_id
            ):
                line.account_id = line.move_id.partner_id.exp_account_id.id
        return res
