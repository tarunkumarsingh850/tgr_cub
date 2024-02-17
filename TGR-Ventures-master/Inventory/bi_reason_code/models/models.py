from odoo import fields, models, api


class ReasonCode(models.Model):
    _name = "reason.code"
    _description = "Reason Code Master"

    code = fields.Char("Code")
    name = fields.Char("Description")

    def name_get(self):
        result = []
        for reason in self:
            if reason.name and reason.code:
                name = reason.name + "-" + str(reason.code)
                result.append((reason.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(
                ["|", ("name", "ilike", name), ("code", "ilike", name)] + args,
                limit=limit,
            )
        if not recs:
            recs = self.search([("name", operator, name)] + args, limit=limit)
        return recs.name_get()
