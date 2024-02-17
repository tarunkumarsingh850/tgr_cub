from odoo import fields, models


class AssignCarrierWizard(models.TransientModel):
    _name = "assign.carrier.wizard"

    delivery_id = fields.Many2one("delivery.carrier", string="Carrier")

    def assign_carrier(self):
        stock_picking = self.env["stock.picking"].browse(self._context.get("active_ids", []))
        for each in stock_picking:
            each.carrier_id = self.delivery_id.id
