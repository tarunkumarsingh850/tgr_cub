from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = "res.company"

    generic_so_default = fields.Boolean("Default company for generic sale order creation")
    dropshipping_shipping_cost = fields.Float(string="Shipping Cost")
    dropshipping_picking_packing_cost = fields.Monetary("Picking/Packing Cost")
    dropshipping_min_pick_pack_cost_upto_sku_count = fields.Integer("Minimum Picking/Packing Cost upto SKU Count")
    dropshipping_additional_picking_packing_cost = fields.Monetary("Additional Picking/Packing Cost")
    dropshipping_payment_surcharge = fields.Monetary("Payment Surcharge")

    @api.constrains("generic_so_default")
    def constrain_company_generic_so_default(self):
        """
        Constrain default company for generic sale order creation from API or XML or CSV
        """
        if (
            self.generic_so_default
            and self.search_count([("id", "!=", self.id), ("generic_so_default", "=", True)]) > 0
        ):
            raise UserError(
                _(
                    "Another default company for generic sale order creation was found. "
                    "Please remove that before setting up this company as the default."
                )
            )
