from odoo import fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_ticket_sale = fields.Boolean(string="Is Ticket Sale", default=False)

    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            if "default_is_ticket_sale" in self.env.context:
                if self.env.context["default_is_ticket_sale"]:
                    vals["name"] = self.env["ir.sequence"].next_by_code("ticket.sales.new") or _("New")
        return super(SaleOrder, self).create(vals)
