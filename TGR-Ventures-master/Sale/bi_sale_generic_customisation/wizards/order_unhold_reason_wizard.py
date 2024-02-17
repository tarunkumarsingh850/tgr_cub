from odoo import models, fields


class OrderUnholdReasonWizard(models.TransientModel):
    _name = "order.unhold.reason.wizard"
    _description = "Order Unhold Reason Wizard"

    order_id = fields.Many2one("sale.order", string="Order")
    hold_type = fields.Selection([("hold", "Hold"), ("unhold", "Unhold")], string="Hold Type", default="hold")
    hold_reason_id = fields.Many2one("hold.reason", string="Hold Reason")
    unhold_reason = fields.Text("Order Hold Override Reason")

    def submit(self):
        if self.hold_type == "hold":
            self.order_id.write({"is_hold": True, "hold_reason_id": self.hold_reason_id.id})
        elif self.hold_type == "unhold":
            self.order_id.write({"is_hold": False, "order_hold_override_reason": self.unhold_reason})
