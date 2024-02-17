from odoo import fields, api, models
import requests
import json


class AccountsPaymentGeneric(models.Model):
    _inherit = "account.payment"

    account_type = fields.Char("Type")

    @api.onchange("partner_id", "name")
    def _onchange_partner_id(self):
        for each in self:
            if each.payment_type == "inbound":
                return {"domain": {"partner_id": [("is_customer", "=", True), ('is_company','=', True)]}}
            elif each.payment_type == "outbound":
                return {"domain": {"partner_id": [("is_supplier", "=", True), ('is_company','=', True)]}}

    def action_post(self):
        res = super(AccountsPaymentGeneric, self).action_post()
        if self.sale_id:
            for picking in self.sale_id.picking_ids:
                picking.payment_status = "paid"
        if (
            self.sale_id.magento_payment_method_id.payment_method_code == "zellepayment"
            and self.sale_id.magento_status == "pending"
            and not self.sale_id.is_payment_posted
        ):
            instance = self.env["magento.instance"].sudo().search([], limit=1)
            headers = {
                "Accept": "*/*",
                "Content-Type": "application/json",
                "User-Agent": "My User Agent 1.0",
                "Authorization": "Bearer {}".format(instance.access_token),
            }
            log_book = self.env["common.log.book.ept"].search([], limit=1)
            if not log_book:
                log_book = self.env["common.log.book.ept"].create({})
            api_url = f"{instance.magento_url}/rest/V1/orders"
            data = {
                "entity": {
                    "entity_id": self.sale_id.magento_order_id,
                    "status": "processing",
                    "increment_id": self.sale_id.name,
                }
            }
            if data:
                response = requests.post(api_url, data=json.dumps(data), headers=headers)
                log_book.write(
                    {
                        "log_lines": [
                            (
                                0,
                                0,
                                {
                                    "message": response.text,
                                    "api_url": api_url,
                                    "api_data_sent": json.dumps(data),
                                },
                            )
                        ]
                    }
                )
            self.sale_id.magento_status = "processing"
            self.sale_id.is_payment_posted = True
        return res

    def _action_cancel_payment(self):
        for line in self:
            line.state = "cancel"
