from odoo import api, fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    taxjar_account_id = fields.Many2one("taxjar.account", "TaxJar Account")

    @api.onchange("taxjar_account_id", "country_id")
    def onchange_taxjar_account_id(self):
        for rec in self:
            if rec.taxjar_account_id:
                rec.auto_apply = True
                rec.country_id = (
                    rec.taxjar_account_id.mapped("state_ids")
                    and rec.taxjar_account_id.mapped("state_ids")[0].country_id.id
                    or False
                )
                rec.state_ids = rec.taxjar_account_id.mapped("state_ids").ids
