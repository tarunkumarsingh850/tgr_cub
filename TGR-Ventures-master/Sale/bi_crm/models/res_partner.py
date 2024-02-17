from odoo import api, models, fields, _
from ast import literal_eval
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"
    _order = "id desc"

    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "confirmed"), ("decline", "Declined")], string="Status", default="draft"
    )
    product_type = fields.Selection(
        [("seed", "Seeds"), ("non_seed", "Non Seeds")], string="Product Type", default="seed"
    )
    personal_identification_no = fields.Char("Personal ID")
    business_identification_no = fields.Char("Business ID")
    type_of_product = fields.Selection([("stocking", "Stocking"), ("non_stocking", "Non Stocking")], string="Type")
    product_category = fields.Selection(
        [("flowering", "Flowering"), ("accessories", "Accessories"), ("seeds", "Seeds")], string="Category"
    )
    customer_website = fields.Char("Customer Website", tracking=True)
    customer_group_id = fields.Many2one("customer.group", "Customer Group", tracking=True)
    current_buyer = fields.Char(string='Current Buyer', tracking=True)
    is_reselling = fields.Boolean(string='Is Reselling', tracking=True, default=False)
    reselling = fields.Char(string='Reselling', tracking=True)
    is_automated_ordering = fields.Boolean(string='Is Automated Ordering', tracking=True, default=False)
    monthly_turnover = fields.Char(string='Monthly Turnover', tracking=True)
    hear_about_us = fields.Char(string='Hear About Us', tracking=True)
    business_since = fields.Char(string='Business Since', tracking=True)
    other_products_to_sell = fields.Char(string='Other Product to sell', tracking=True)
    current_selling_area = fields.Char(string='Current Selling Area', tracking=True)
    brand_interested = fields.Char(string='Brand Interested', tracking=True)
    type_of_business = fields.Char(string='Type Of Business', tracking=True)
    interested_in_banking = fields.Boolean(string='Interested In Banking', tracking=True, default=False)
    sms_notify = fields.Boolean('SMS Notify', tracking=True, default=False)
    receive_tracking_sms = fields.Boolean('Receive Tracking SMS', tracking=True, default=False)
    receive_marketing_sms = fields.Boolean('Receive Marketing SMS', tracking=True, default=False)
    magento_company_id = fields.Char('Magento Company id')

    # @api.model
    # def create(self, vals):
    #     res = super(ResPartner, self).create(vals)
    #     result = self.env["ir.config_parameter"].sudo().get_param("bi_crm.res_user_id")
    #     if not result:
    #         raise UserError(_("Please configure email"))
    #     result = literal_eval(result)
    #     result = self.env["res.users"].search([("id", "=", result)])
    #     account_application_template = self.env.ref("bi_crm.application_create_email_template")
    #     account_application_template.write({"email_to": res.email, "email_from": result.email})
    #     self.env["mail.template"].browse(account_application_template.id).send_mail(res.id, force_send=True)
    #     return res

    def action_confirm(self):
        pass
        # user_id = self.env["ir.config_parameter"].sudo().get_param("bi_crm.res_user_id")
        # if not user_id:
        #     raise UserError(_("Please configure email"))
        # user_id = literal_eval(user_id)
        # user_id = self.env["res.users"].search([("id", "=", user_id)])
        # account_success_template = self.env.ref("bi_crm.account_success_email_template")
        # account_success_template.write({"email_to": self.email, "email_from": user_id.email})
        # self.env["mail.template"].browse(account_success_template.id).send_mail(self.id, force_send=True)
        # self.write({"state": "confirm"})

    def button_send_mail(self):
        pass
        # user_id = self.env["ir.config_parameter"].sudo().get_param("bi_crm.res_user_id")
        # if not user_id:
        #     raise UserError(_("Please configure email"))
        # user_id = literal_eval(user_id)
        # user_id = self.env["res.users"].search([("id", "=", user_id)])
        # vat_template = self.env.ref("bi_crm.insufficient_vat_email_template")
        # vat_template.write({"email_to": self.email, "email_from": user_id.email})
        # self.env["mail.template"].browse(vat_template.id).send_mail(self.id, force_send=True)
        # return {
        #     "effect": {
        #         "fadeout": "slow",
        #         "message": "Succesfully Mailed!",
        #         "img_url": "/web/static/img/smile.svg",
        #         "type": "rainbow_man",
        #     }
        # }

    def action_decline(self):
        pass
        # user_id = self.env["ir.config_parameter"].sudo().get_param("bi_crm.res_user_id")
        # if not user_id:
        #     raise UserError(_("Please configure email"))
        # user_id = literal_eval(user_id)
        # user_id = self.env["res.users"].search([("id", "=", user_id)])
        # template_no_region = self.env.ref("bi_crm.no_region_email_template")
        # template_no_region.write({"email_to": self.email, "email_from": user_id.email})
        # self.env["mail.template"].browse(template_no_region.id).send_mail(self.id, force_send=True)
        # self.write({"state": "decline"})

    def action_invalid_personal_id(self):
        pass
        # user_id = self.env["ir.config_parameter"].sudo().get_param("bi_crm.res_user_id")
        # if not user_id:
        #     raise UserError(_("Please configure email"))
        # user_id = literal_eval(user_id)
        # user_id = self.env["res.users"].search([("id", "=", user_id)])
        # template = self.env.ref("bi_crm.insufficient_personal_id_email_template")
        # template.write({"email_to": self.email, "email_from": user_id.email})
        # self.env["mail.template"].browse(template.id).send_mail(self.id, force_send=True)
        # return {
        #     "effect": {
        #         "fadeout": "slow",
        #         "message": "Succesfully Mailed!",
        #         "img_url": "/web/static/img/smile.svg",
        #         "type": "rainbow_man",
        #     }
        # }

    def action_invalid_business_id(self):
        pass
        # user_id = self.env["ir.config_parameter"].sudo().get_param("bi_crm.res_user_id")
        # user_id = literal_eval(user_id)
        # if not user_id:
        #     raise UserError(_("Please configure email"))
        # user_id = self.env["res.users"].search([("id", "=", user_id)])
        # template = self.env.ref("bi_crm.insufficient_business_id_email_template")
        # template.write({"email_to": self.email, "email_from": user_id.work_email})
        # # self.env["mail.template"].browse(template.id).send_mail(self.id, force_send=True)
        # return {
        #     "effect": {
        #         "fadeout": "slow",
        #         "message": "Succesfully Mailed!",
        #         "img_url": "/web/static/img/smile.svg",
        #         "type": "rainbow_man",
        #     }
        # }
