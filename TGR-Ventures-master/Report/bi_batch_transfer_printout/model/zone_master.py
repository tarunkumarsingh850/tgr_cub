from odoo import fields, models


class ZoneMaster(models.Model):
    _name = "zone.master"
    _description = "Model for zone master"
    _rec_name = "name"

    name = fields.Char(
        string="Name",
    )
    number = fields.Integer(
        string="Number",
    )
    brand_ids = fields.Many2many(
        string="Brand",
        comodel_name="product.breeder",
    )
    is_product = fields.Boolean(
        string="Is Product",
    )
    product_ids = fields.Many2many(
        string="Products",
        comodel_name="product.product",
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
    )

    is_mixed = fields.Boolean(string="Is Mixed", default=False)
    location_id = fields.Many2one(string="Location", comodel_name="stock.location", domain=[("usage", "=", "internal")])

    _sql_constraints = [
        (
            "_unique_number_constraint",
            "unique(number)",
            "Number must be unique",
        )
    ]
