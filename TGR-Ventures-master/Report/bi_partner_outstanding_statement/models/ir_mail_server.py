from odoo import fields, models


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    is_outstanding_statement_mail = fields.Boolean("Is Outstanding statement Report Mail")
    # outstanding_statement_mail_to = fields.Many2many('res.partner', string='Outstanding Statement mail To', default = lambda self :self.get_partner_id(), domain="[('credit', '>', 0)]")

    # @api.model
    # def get_partner_id(self):
    #     partner_obj = self.env['res.partner'].search([('credit', '>', 0), ('customer_class_id.is_wholesales', '=', True)])
    #     return partner_obj
