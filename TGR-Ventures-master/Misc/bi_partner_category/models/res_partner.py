from odoo import fields, models, _, api
from datetime import date, timedelta
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    res_partner_line_ids = fields.One2many(
        "partner.category.line", "res_partner_category_id", string="Partner Category Lines"
    )

    def Check_document_reminder(self):
        partner_category = self.env["partner.category.line"].search([])
        for rec in partner_category:
            if rec.reminder and rec.end_date:
                end_date = rec.end_date
                today = date.today()
                days = end_date - timedelta(days=rec.reminder)
                if today == days:
                    model = self.env["ir.model"].search([("model", "=", "partner.category.line")])
                    reminder_id = self.env["reminder.user"].search([])
                    for line in reminder_id.reminder_user_line_ids:
                        activity_id = self.env["mail.activity.type"].search(
                            [("name", "=", "Partner Document Reminder")]
                        )
                        data = {
                            "res_id": rec.id,
                            "res_model_id": model.id,
                            "user_id": line.users_id.id,
                            "summary": ("Reminder for %s" % rec.partner_category_id.name),
                            "activity_type_id": activity_id.id,
                        }
                        self.env["mail.activity"].create(data)


class PartnerCategoryLine(models.Model):
    _name = "partner.category.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    res_partner_category_id = fields.Many2one("res.partner", string="Partner ID")
    partner_category_id = fields.Many2one("partner.category", string="Partner Category")
    start_date_ = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    reminder = fields.Integer(string="Reminder(Days)")
    attachment_id = fields.Many2many(
        "ir.attachment",
        "doc_attach_rel",
        "doc_id",
        "attach_id3",
        string="Attachment",
        copy=False,
    )

    @api.onchange("start_date_", "end_date")
    def _onchange_start_date(self):
        if self.start_date_ and self.end_date:
            if self.start_date_ > self.end_date:

                raise UserError(_("Start date will be less than End date"))
