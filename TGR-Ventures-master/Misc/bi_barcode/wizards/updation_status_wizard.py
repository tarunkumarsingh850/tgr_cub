from odoo import fields, models


class UpdationStatusWizard(models.TransientModel):
    _name = "updation.status"
    _description = "Status of Errored Product Other Details Updation"

    # note = self.env.context.get('note')
    message = fields.Char(string="Status")
