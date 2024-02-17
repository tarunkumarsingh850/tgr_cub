from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DespatchlabProduct(models.Model):
    _name = "despatchlab.product"
    _description = "Despatchlab Product"

    odoo_product_sku = fields.Char("Odoo Product SKU")
    despatchlab_product_id = fields.Char("Despatchlab Product ID")

    @api.constrains("odoo_product_sku")
    def _constrains_sku_id(self):
        for rec in self:
            is_exists = self.env["despatchlab.product"].search(
                [("odoo_product_sku", "=", rec.odoo_product_sku), ("id", "!=", rec.id)]
            )
            if is_exists:
                raise UserError(_(f"Despatchlab product ID exists for the product sku {is_exists.odoo_product_sku}."))
