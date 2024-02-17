from odoo import _, fields, models
from twilio.rest import Client
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_send_sms = fields.Boolean("Is Send SMS", default=False)

    def send_sms(self):
        phone = ""
        for picking in self:
            if picking.partner_id.phone:
                phone = picking.partner_id.phone
            else:
                if picking.parent_id.partner_id.phone:
                    phone = picking.parent_id.partner_id.phone
            if not phone:
                raise UserError(_("Please add customer Phone Numner"))
            if not picking.carrier_tracking_ref:
                raise UserError(_("Tracking reference not available."))
            account_sid = self.env["ir.config_parameter"].sudo().get_param("bi_sms_gateway.account_sid")
            account_auth_token = self.env["ir.config_parameter"].sudo().get_param("bi_sms_gateway.account_auth_token")
            from_number = self.env["ir.config_parameter"].sudo().get_param("bi_sms_gateway.from_number")
            if not picking.is_send_sms:
                if account_sid and account_auth_token and from_number:
                    account_sid = account_sid
                    auth_token = account_auth_token
                    client = Client(account_sid, auth_token)

                    message = client.messages.create(
                        from_=from_number,
                        body="{}: We are glad to inform you that your order n° {}  has been shipped. {}: We are glad to inform you that your order has been shipped. Your tracking reference is {}".format(
                            picking.company_id.name,
                            picking.origin if picking.origin else "",
                            picking.company_id.name,
                            picking.carrier_tracking_ref if picking.carrier_tracking_ref else "",
                        ),
                        to=phone,
                    )
                    if message:
                        picking.is_send_sms = True
                else:
                    raise UserError(_("Please configure your SMS Gateway"))
