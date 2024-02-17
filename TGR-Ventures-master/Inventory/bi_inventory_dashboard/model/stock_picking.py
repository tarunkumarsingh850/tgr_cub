from odoo import models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        result = super(StockPicking, self).button_validate()
        for record in self:
            if record.is_hold:
                raise UserError(_("You Cannot validate order '%s' which is in On-hold.") % (record.origin))
        return result
