from odoo import fields, models


class CancelWizard(models.TransientModel):
    _name = "picking.cancel"
    _description = "Picking Cancel Wizard"

    reason = fields.Char("Reason")
    picking_id = fields.Many2one("stock.picking", string="")

    def confirm(self):
        for picking in self.picking_id:
            picking.is_cancel = True
            picking.reason = self.reason
            # if picking.magento_shipping_id:
            #     BASE_URL = f"{picking.magento_instance_id.magento_url}/rest/V1/orders/{picking.magento_shipping_id}/comments"
            #     headers = {"Content-type": "application/json", "Authorization": "Bearer 8j1fygjbqn8nwt6polxk54ykmvdquj4d"}
            #     cancel_date = datetime.strftime(datetime.today(), "%Y-%m-%d")
            #     cancel_time = f"{datetime.today().hour}:{datetime.today().minute}:{datetime.today().second}"
            #     param = {
            #         "statusHistory": {
            #             "comment": f"Delivery Cancelled due to {picking.reason}",
            #             "created_at": f"{cancel_date} {cancel_time}",
            #             "parent_id": 54,
            #             "is_customer_notified": 0,
            #             "is_visible_on_front": 1,
            #             "status": "pending",
            #         }
            #     }
            #     requests.post(BASE_URL, json=param, headers=headers)
