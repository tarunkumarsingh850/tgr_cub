from odoo import fields, models


class SaleType(models.Model):
    _name = "sale.type"
    _description = "Sale Type Master"
    _rec_name = "code"

    _sql_constraints = [("code", "UNIQUE (code)", "Code should be unique!")]

    name = fields.Char("Name", required="1")
    code = fields.Char("Code", required="1")
