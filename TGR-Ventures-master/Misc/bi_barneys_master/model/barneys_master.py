from odoo import fields, models


class BarneysMaster(models.Model):
    _name = "barneys.master"
    _description = "Module is used to store barneys data"
    _rec_name = "odoo_sku"

    odoo_sku = fields.Char(
        string="Odoo Sku",
    )
    barneys_sku = fields.Char(
        string="Barneys Sku",
    )
    selling_price = fields.Float(
        string="Selling Price",
    )

    _sql_constraints = [
        (
            "unique_odoo_sku",
            "unique(odoo_sku, barneys_sku)",
            "SKU is already used. SKU must be Unique!",
        )
    ]
