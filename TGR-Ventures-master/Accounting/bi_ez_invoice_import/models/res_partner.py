from odoo import fields, models,_

class ResPartner(models.Model):
    _inherit= 'res.partner'

    is_ez_import_customer = fields.Boolean('Is EZ Import Customer')