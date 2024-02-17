from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTag(models.Model):
    _name = "product.tag"
    _description = "Product Tag"

    name = fields.Char("Name")
    is_usa = fields.Boolean("Is USA")
    is_eu_uk = fields.Boolean("Is EU and UK")

    @api.constrains("name")
    def _constrains_name(self):
        for tag in self:
            is_exists = self.env["product.tag"].search([("id", "!=", tag.id), ("name", "ilike", tag.name)])
            if is_exists:
                raise UserError(_(f"Tag with name {tag.name} already exists."))
