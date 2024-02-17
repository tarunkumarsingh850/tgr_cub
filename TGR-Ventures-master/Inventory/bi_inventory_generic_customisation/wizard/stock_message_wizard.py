from odoo import fields, models


class ShMessageWizard(models.TransientModel):
    _name = "shock.message.wizard"

    def get_default(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    name = fields.Text(string="Message", readonly=True, default=get_default)

    def validation_continue(self):
        active_id = self.env.context.get("active_id")
        active_model = self.env.context.get("active_model")
        if active_model == "stock.picking":
            picking_id = self.env[active_model].browse(active_id)
            return picking_id.with_context(is_tracking_ref_msg=False).button_validate()
        if active_model == "stock.picking.batch":
            picking_batch_id = self.env[active_model].browse(active_id)
            return picking_batch_id.picking_ids.with_context(is_tracking_ref_msg=False).button_validate()
