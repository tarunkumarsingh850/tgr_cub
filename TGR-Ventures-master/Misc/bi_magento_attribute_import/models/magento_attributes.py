from odoo import fields, models


class MagentoAttribute(models.Model):
    _name = "magento.attribute"
    _description = "Model is used to store the magento attribute"
    _rec_name = "name"

    name = fields.Char(string="Name", required="1")
    code = fields.Char(string="Code", required="1")

    _sql_constraints = [
        (
            "unique_magento_attribute_code",
            "unique(code)",
            "This delivery carrier code is already exists",
        )
    ]
