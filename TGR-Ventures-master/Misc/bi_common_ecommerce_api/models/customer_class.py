from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CustomerClass(models.Model):
    _inherit = "customer.class"
    _description = "Customer Class"

    is_dutch_customer = fields.Boolean("Is Dutchs Customer")

    @api.onchange("is_dutch_customer")
    def _onchange_is_dutch_customer(self):
        customer_class = self.env["customer.class"]
        if self.is_dutch_customer == True:
            record = customer_class.search([("is_dutch_customer", "=", True)])
            if record:
                raise UserError(_("Dutchs Customer is already assigned"))
