from odoo import api, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    @api.model
    def _action_product_pricelist_check(self):
        for rec in self.search([]):
            for item in rec.item_ids:
                if (
                    item.product_tmpl_id.is_pending_discontinued
                    or item.product_tmpl_id.is_free_product
                    or item.product_tmpl_id.wholesale_price_value == 0.00
                ):
                    rec.item_ids = [(3, item.id)]
