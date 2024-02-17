from odoo import models


class MagentoProductProduct(models.Model):
    _inherit = "magento.product.product"

    def _prepare_product_values(self, link):
        values = super(MagentoProductProduct, self)._prepare_product_values(link)
        inventory_account_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("bi_inventory_generic_customisation.product_inventory_account_id")
        )
        if inventory_account_id:
            values.update({"account_inventory_id": int(inventory_account_id)})
        return values
