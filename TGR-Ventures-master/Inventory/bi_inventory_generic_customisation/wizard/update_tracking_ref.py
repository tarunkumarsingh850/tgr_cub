from odoo import fields, models


class UpdateTrackingWizard(models.TransientModel):
    _name = "tracking.reference.wizard"
    _description = "Tracking Reference Wizard"

    stock_picking_id = fields.Many2one("stock.picking")
    tracking_ref = fields.Char(string="Tracking Reference")

    def confirm(self):
        self.stock_picking_id.carrier_tracking_ref = self.tracking_ref
