# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_customer = fields.Boolean(
        compute="_compute_is_customer",
        inverse="_inverse_is_customer",
        store=True,
        readonly=False,
        string="Is a Customer",
    )
    is_supplier = fields.Boolean(
        compute="_compute_is_supplier",
        inverse="_inverse_is_supplier",
        store=True,
        readonly=False,
        string="Is a Supplier",
    )
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")

    @api.depends("customer_rank")
    def _compute_is_customer(self):
        for partner in self:
            if bool(partner.customer_rank):
                partner.is_customer = bool(partner.customer_rank)
            elif not bool(partner.customer_rank) and partner.invoice_ids:
                partner.is_customer = True
            else:
                partner.is_customer = False

    @api.depends("supplier_rank")
    def _compute_is_supplier(self):
        for partner in self:
            partner.is_supplier = bool(partner.supplier_rank)

    def _inverse_is_customer(self):
        for partner in self:
            partners = partner | partner.commercial_partner_id
            if partner.is_customer:
                partners._increase_rank("customer_rank")
            else:
                partners.customer_rank = 0

    def _inverse_is_supplier(self):
        for partner in self:
            partners = partner | partner.commercial_partner_id
            if partner.is_supplier:
                partners._increase_rank("supplier_rank")
            else:
                partners.supplier_rank = 0

    # Commented for migration purpose
    # def name_get(self):
    #     result = []
    #     for partner in self:
    #         if partner.is_customer:
    #             name = partner.name + "-" + str(partner.customer_code)
    #             result.append((partner.id, name))
    #         elif partner.is_supplier:
    #             name = partner.name + "-" + str(partner.vendor_code)
    #             result.append((partner.id, name))
    #     return result

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(
                ["|", "|", ("name", "ilike", name), ("customer_code", "ilike", name), ("vendor_code", "ilike", name)]
                + args,
                limit=limit,
            )
        if not recs:
            recs = self.search([("name", operator, name)] + args, limit=limit)
        return recs.name_get()
