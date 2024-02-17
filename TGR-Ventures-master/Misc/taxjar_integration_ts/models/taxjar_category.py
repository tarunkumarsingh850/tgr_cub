from odoo import fields, models


class TaxjarCategory(models.Model):
    _name = "taxjar.category"
    _description = "TaxJar Category"

    name = fields.Char("Name", required=True)
    product_tax_code = fields.Char("Tax Code")
    description = fields.Char("Description")
    account_id = fields.Many2one("taxjar.account", string="TaxJar Account")
