from odoo import api, fields, models


class TicketTicket(models.Model):
    _name = "ticket.ticket"
    _description = "Module is used to store ticket data"
    _rec_name = "name"

    @api.model
    def _get_default_company_id(self):
        """Get the default company."""
        return self.env.company.id

    @api.model
    def _get_default_currency(self):
        """Get the default currency from company."""
        return self.company_id.currency_id.id

    name = fields.Char(string="Number", copy=False, readonly=True, store=True, index=True, tracking=True, default="/")
    date = fields.Date(
        string="Date",
        required=True,
        index=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
        tracking=True,
        default=fields.Date.context_today,
    )
    ref = fields.Char(string="Reference", copy=False, tracking=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("posted", "Posted"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default="draft",
    )
    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", store=True, default=_get_default_company_id
    )
    currency_id = fields.Many2one(
        "res.currency",
        store=True,
        readonly=True,
        tracking=True,
        required=True,
        states={"draft": [("readonly", False)]},
        string="Currency",
        default=lambda self: self.env.company.currency_id.id,
    )
    line_ids = fields.One2many(
        "ticket.ticket.line", "ticket_id", string="Ticket Lines", copy=True, states={"draft": [("readonly", False)]}
    )
    partner_id = fields.Many2one(
        "res.partner",
        readonly=True,
        tracking=True,
        states={"draft": [("readonly", False)]},
        check_company=True,
        string="Customer",
    )

    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        states={"draft": [("readonly", False)]},
        domain="[('type', 'in',('cash','bank'))]",
    )

    # === Amount fields ===
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        store=True,
        readonly=True,
        tracking=True,
    )
    amount_tax = fields.Monetary(
        string="Tax",
        store=True,
        readonly=True,
    )
    amount_total = fields.Monetary(string="Total", store=True, readonly=True, compute="_compute_amount")

    partner_shipping_id = fields.Many2one(
        "res.partner",
        string="Delivery Address",
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Delivery address for current invoice.",
    )

    def action_post(self):
        for rec in self:
            if rec.name == "/":
                sequence_code = "ticket.ticket"
                rec.name = self.env["ir.sequence"].next_by_code(sequence_code, sequence_date=rec.date)
                rec.state = "posted"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"

    @api.depends("line_ids")
    def _compute_amount(self):
        for rec in self:
            amount_total = 0
            amount_tax = 0
            amount_untaxed = 0
            if rec.line_ids:
                for line in rec.line_ids:
                    amount_total += line.price_total
                    amount_untaxed += line.price_subtotal
            amount_tax = amount_total - amount_untaxed
            rec.amount_untaxed = amount_untaxed
            rec.amount_tax = amount_tax
            rec.amount_total = amount_total


class TicketTicketLine(models.Model):
    _name = "ticket.ticket.line"
    _description = "Module is used to store ticket line data"

    ticket_id = fields.Many2one("ticket.ticket", string="Ticket Entry", index=True, required=True, ondelete="cascade")

    date = fields.Date(related="ticket_id.date", store=True, index=True, copy=False)
    parent_state = fields.Selection(related="ticket_id.state", store=True)
    company_id = fields.Many2one(related="ticket_id.company_id", store=True)
    display_type = fields.Selection(
        [
            ("line_section", "Section"),
            ("line_note", "Note"),
        ],
        default=False,
        help="Technical field for UX purpose.",
    )
    name = fields.Char(string="Label", tracking=True)
    quantity = fields.Float(
        string="Quantity",
        default=1.0,
        digits="Product Unit of Measure",
        help="The optional quantity expressed by this line, eg: number of product sold. "
        "The quantity is not a legal requirement but is very useful for some reports.",
    )
    price_unit = fields.Float(string="Unit Price", digits="Product Price")
    amount_subtotal = fields.Monetary(
        string="Subtotal", store=True, currency_field="currency_id", compute="_compute_amount_line"
    )
    price_subtotal = fields.Monetary(
        string="Subtotal", store=True, currency_field="currency_id", compute="_compute_amount_line"
    )
    price_total = fields.Monetary(
        string="Total", store=True, currency_field="currency_id", compute="_compute_amount_line"
    )
    date_maturity = fields.Date(
        string="Due Date",
        index=True,
        tracking=True,
        help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.",
    )
    currency_id = fields.Many2one("res.currency", string="Currency", required=True, related="ticket_id.currency_id")
    partner_id = fields.Many2one("res.partner", string="Partner", ondelete="restrict")
    product_uom_id = fields.Many2one("uom.uom", string="Unit of Measure", ondelete="restrict")
    product_id = fields.Many2one("product.product", string="Product", ondelete="restrict")
    tax_ids = fields.Many2many(
        comodel_name="account.tax",
        string="Taxes",
        context={"active_test": False},
        domain=[("type_tax_use", "=", "sale")],
        help="Taxes that apply on the base amount",
    )

    def _get_computed_uom(self):
        self.ensure_one()
        if self.product_id:
            return self.product_id.uom_id
        return False

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            line.name = line.product_id.name
            line.product_uom_id = line._get_computed_uom()

    @api.depends("tax_ids", "price_unit", "quantity")
    def _compute_amount_line(self):
        for line in self:
            taxes_res = line.tax_ids.compute_all(
                line.price_unit,
                quantity=line.quantity,
                currency=line.ticket_id.currency_id,
                product=line.product_id,
                partner=line.ticket_id.partner_id,
                is_refund=False,
            )
            line.price_subtotal = taxes_res["total_excluded"]
            line.price_total = taxes_res["total_included"]
            line.amount_subtotal = line.quantity * line.price_unit
