from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _update_product_replenishment(self):
        product_id = self.env["product.product"].search([])
        for each in product_id:
            stock_warehouse_id = self.env["stock.warehouse.orderpoint"].search([("product_id", "=", each.id)])
            if not stock_warehouse_id:
                product_tmpl_id = self.env["product.template"].search([("id", "=", each.product_tmpl_id.id)])
                self.env["stock.warehouse.orderpoint"].create(
                    {
                        "product_id": each.id,
                        "route_id": 5,
                        "supplier_id": product_tmpl_id.seller_ids[0].id if product_tmpl_id.seller_ids else False,
                    }
                )
