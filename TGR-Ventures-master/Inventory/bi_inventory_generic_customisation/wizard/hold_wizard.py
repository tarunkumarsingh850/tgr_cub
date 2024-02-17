from odoo import fields, models


class HoldWizard(models.TransientModel):
    _name = "picking.hold"
    _description = "Picking Hold Wizard"

    hold_reason_id = fields.Many2one("hold.reason", string="Hold Reason")
    picking_ids = fields.Many2many("stock.picking", "hold_picking_rel", string="")

    def confirm(self):
        for picking in self.picking_ids:
            picking.is_hold = True
            picking.hold_reason_id = self.hold_reason_id.id
