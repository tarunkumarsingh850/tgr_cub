from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    dropshipping_code = fields.Char("Dropshipping Code")

    @api.constrains("dropshipping_code")
    def _constrains_dropshipping_code(self):
        for warehouse in self:
            is_exists = self.env["stock.warehouse"].search(
                [("id", "!=", warehouse.id), ("dropshipping_code", "ilike", warehouse.dropshipping_code)]
            )
            if warehouse.dropshipping_code and is_exists:
                raise UserError(_(f"Warehouse with dropshipping code {warehouse.dropshipping_code} already exists."))
