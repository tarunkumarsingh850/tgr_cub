from odoo import models, fields


class PackSizeConfigurable(models.Model):
    _name = "pack.size.configurable"
    _rec_name = "name"

    name = fields.Char(
        string="Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )

    _sql_constraints = [("unique_code", "unique (code)", "Code should be unique !")]
