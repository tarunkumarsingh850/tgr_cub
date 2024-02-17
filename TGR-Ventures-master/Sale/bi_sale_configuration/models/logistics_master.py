from odoo import fields, models


class BiLogisticsMaster(models.Model):
    _name = "bi.logistics.master"
    _description = "Logistics master"
    _rec_name = "name"

    name = fields.Char(
        string="Name",
    )
    street = fields.Char("street")
    street2 = fields.Char()
    zip = fields.Char("Zip")
    city = fields.Char("City")
    state_id = fields.Many2one("res.country.state", domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one("res.country")
    email = fields.Char()
    phone = fields.Char()
    vat = fields.Char("Vat")
