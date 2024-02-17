from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    synchronize_product_price = fields.Boolean(string="Synchronize Product Price", default=False)
