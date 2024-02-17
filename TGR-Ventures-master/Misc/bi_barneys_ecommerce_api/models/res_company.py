from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"
    _description = "Res Company"

    shipping_cost_product_id = fields.Many2one("product.template", string="Shipping Cost Product")
    picking_packing_cost = fields.Monetary("Picking/Packing Cost")
    min_pick_pack_cost_upto_sku_count = fields.Integer("Minimum Picking/Packing Cost upto SKU Count")
    additional_picking_packing_cost = fields.Monetary("Additional Picking/Packing Cost")
    barneys_payment_surcharge = fields.Monetary("Payment Surcharge")
    tgr_percentage = fields.Float("TGR Percentage")
    barneys_percentage = fields.Float("Barneys Percentage")
