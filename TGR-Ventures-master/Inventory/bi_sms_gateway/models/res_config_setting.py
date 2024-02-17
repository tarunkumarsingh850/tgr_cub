from odoo import fields, models


class ResConfigSetting(models.TransientModel):
    _inherit = "res.config.settings"

    account_sid = fields.Char("Account sid", config_parameter="bi_sms_gateway.account_sid")
    account_auth_token = fields.Char("Account Auth Token", config_parameter="bi_sms_gateway.account_auth_token")
    from_number = fields.Char("From", config_parameter="bi_sms_gateway.from_number")
