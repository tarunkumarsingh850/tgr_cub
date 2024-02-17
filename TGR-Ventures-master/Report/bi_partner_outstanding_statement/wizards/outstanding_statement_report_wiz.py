from odoo import api, fields, models
import datetime


class OutstandingStatementReport(models.TransientModel):
    _name = "outstanding.statement.report.wiz"

    name = fields.Char()
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        string="Company",
        required=True,
    )
    date_end = fields.Date(required=True, default=fields.Date.context_today)
    show_aging_buckets = fields.Boolean(default=True)
    number_partner_ids = fields.Integer(default=lambda self: len(self._context["active_ids"]))
    filter_partners_non_due = fields.Boolean(string="Don't show partners with no due entries", default=True)
    filter_negative_balances = fields.Boolean("Exclude Negative Balances", default=True)

    aging_type = fields.Selection(
        [("days", "Age by Days"), ("months", "Age by Months")],
        string="Aging Method",
        default="days",
        required=True,
    )

    account_type = fields.Selection(
        [("receivable", "Receivable"), ("payable", "Payable")],
        default="receivable",
    )
    partner_ids = fields.Many2many("res.partner", default=lambda self: self.get_partner_id())

    @api.model
    def get_partner_id(self):
        active_ids = "active_ids" in self._context and self._context["active_ids"] or []
        if active_ids:
            partner_obj = self.env["res.partner"].browse(active_ids)
        else:
            partner_obj = self.env["res.partner"].search(
                [("credit", ">", 0), ("customer_class_id.is_wholesales", "=", True)]
            )
        return partner_obj

    def print_report(self, report_type="qweb-web"):
        self.ensure_one()
        data = self._prepare_statement()
        report_name = "bi_partner_outstanding_statement.action_print_outstanding_statement_report"
        return self.env.ref(report_name).report_action(self, data=data)

    def _prepare_statement(self):
        self.ensure_one()
        return {
            "date_end": self.date_end,
            "company_id": self.company_id.id,
            "partner_ids": "active_ids" in self._context
            and self._context["active_ids"]
            or self._context["partner_ids"],
            "show_aging_buckets": self.show_aging_buckets,
            "filter_non_due_partners": self.filter_partners_non_due,
            "account_type": self.account_type,
            "aging_type": self.aging_type,
            "filter_negative_balances": self.filter_negative_balances,
        }

    @api.model
    def send_outstanding_statement_report(self):
        current_day = datetime.datetime.now().day
        if current_day == 30:
            outgoing_mail = self.env["ir.mail_server"].search([("is_outstanding_statement_mail", "=", True)], limit=1)
            outstanding_statement_mail_to = self.env["res.partner"].search(
                [("credit", ">", 100), ("customer_class_id.is_wholesales", "=", True)]
            )
            for partner in outstanding_statement_mail_to:
                template = self.env.ref("bi_partner_outstanding_statement.email_template_name")
                template.email_from = outgoing_mail.smtp_user
                template.email_to = partner.email
                if "partner_ids" not in self._context:
                    wiz = self.env["outstanding.statement.report.wiz"].with_context(
                        active_ids=partner.ids, partner_ids=partner.ids, model="res.partner"
                    )
                    self._context.update(wiz.create({})._prepare_statement())
                else:
                    wiz = self.env["outstanding.statement.report.wiz"].with_context(
                        active_ids=partner.ids, partner_ids=partner.ids, model="res.partner"
                    )
                    self._context.update(wiz.create({})._prepare_statement())
                template.report_template = self.env.ref(
                    "bi_partner_outstanding_statement.action_print_outstanding_statement_report"
                )
                template.send_mail(self.id, force_send=True)
