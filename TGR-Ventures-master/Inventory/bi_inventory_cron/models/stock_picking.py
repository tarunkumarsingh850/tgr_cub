from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_update_state_picking(self):
        for rec in self.env['stock.picking'].search([('is_shopify_delivery_order','=',True), ('carrier_tracking_ref','!=', False),('state','=','confirmed')]):
            rec.state = 'done'