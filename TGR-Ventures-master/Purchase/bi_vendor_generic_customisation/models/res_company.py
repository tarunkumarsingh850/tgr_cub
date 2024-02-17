from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    synchronize_vendor_taxes = fields.Boolean("Synchronize Vendor Taxes", default=False)
