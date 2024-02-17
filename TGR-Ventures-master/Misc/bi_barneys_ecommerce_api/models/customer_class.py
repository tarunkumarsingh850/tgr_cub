from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CustomerClass(models.Model):
    _inherit = "customer.class"
    _description = "Customer Class"

    is_barneys_customer = fields.Boolean("Is Barneys Customer")

    @api.onchange("is_barneys_customer")
    def _onchange_is_barneys_customer(self):
        customer_class = self.env["customer.class"]
        if self.is_barneys_customer == True:
            record = customer_class.search([("is_barneys_customer", "=", True)])
            if record:
                raise UserError(_("Barneys Customer is already assigned"))
