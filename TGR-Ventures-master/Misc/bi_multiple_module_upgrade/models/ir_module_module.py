from odoo import api, models


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(["|", ("shortdesc", "ilike", name), ("name", "ilike", name)] + args, limit=limit)
        if not recs:
            recs = self.search([("name", operator, name)] + args, limit=limit)
        return recs.name_get()
