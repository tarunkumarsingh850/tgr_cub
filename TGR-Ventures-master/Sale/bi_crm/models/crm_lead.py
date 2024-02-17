from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    is_wholesale_account = fields.Selection([("yes", "Yes"), ("no", "No Region")], string="Is Wholesale Account")
    type_ = fields.Selection([("stocking", "Stocking"), ("non_stocking", "Non Stocking")], string="Type")
    # def button_send_email(self):
    #     template = self.env.ref("bi_crm.insufficient_personal_id_email_template")
    #     crm_ids = self.env["crm.lead"].search([])
    #     user_id = self.env["res.users"].search([("id", "=", 2)])
