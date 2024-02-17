from odoo import fields, models,api, _

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    @api.model
    def create(self, vals):
        res = super(StockLandedCost,self).create(vals)
        picking_id = res.vendor_bill_id.invoice_line_ids.purchase_line_id.order_id.picking_ids.filtered(lambda p : p.state == 'done')
        if picking_id:
            res.picking_ids = [(6,0,picking_id.ids)]
        return res