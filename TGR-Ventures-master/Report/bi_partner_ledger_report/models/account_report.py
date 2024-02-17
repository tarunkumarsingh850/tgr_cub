from odoo import models


class AccountReport(models.AbstractModel):
    _inherit = "account.report"

    filter_salesperson = None

    def _init_filter_salesperson(self, options, previous_options=None):
        if not self.filter_salesperson:
            return

        options["salesperson"] = True

        options["user_id"] = (previous_options or {}).get("user_id", [])
        return options

    def _set_context(self, options):
        ctx = super(AccountReport, self)._set_context(options)
        if options.get("user_id"):
            ctx["user_id"] = self.env["res.users"].browse(tuple(options.get("user_id")))
        return ctx
