from odoo import fields, models
import requests
from datetime import datetime


class OrderCancel(models.TransientModel):
    _name = "cancel.sale"
    _description = "Sale Order Cancel"

    reason = fields.Char(string="Reason", required=True)
    sale_id = fields.Many2one("sale.order", string="")

    def confirm(self):
        for order in self:
            order.sale_id.cancel_reason = order.reason
            order.sale_id.is_cancel_reason = True
            order.sale_id.state = "cancel"
            if order.sale_id.magento_order_id:
                BASE_URL = f"{self.sale_id.magento_instance_id.magento_url}/rest/V1/orders/{self.sale_id.magento_order_id}/comments"
                headers = {
                    "Content-type": "application/json",
                    "Authorization": "Bearer 8j1fygjbqn8nwt6polxk54ykmvdquj4d",
                }
                cancel_date = datetime.strftime(datetime.today(), "%Y-%m-%d")
                cancel_time = f"{datetime.today().hour}:{datetime.today().minute}:{datetime.today().second}"
                param = {
                    "statusHistory": {
                        "comment": f"Order Cancelled due to {order.reason}",
                        "created_at": f"{cancel_date} {cancel_time}",
                        "parent_id": 54,
                        "is_customer_notified": 0,
                        "is_visible_on_front": 1,
                        "status": "pending",
                    }
                }
                requests.post(BASE_URL, json=param, headers=headers)
