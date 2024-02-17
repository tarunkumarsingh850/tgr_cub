from odoo import models, fields, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    bom_number = fields.Integer(string="Bill of Material", compute="_compute_bom_number")

    def _compute_bom_number(self):
        for rec in self:
            bom_count = self.env["bill.material"].search_count([("product_id.product_tmpl_id", "=", rec.id)])
            rec.bom_number = bom_count

    def action_view_bom(self):
        bom_count = self.env["bill.material"].search([("product_id.product_tmpl_id", "=", self.id)])
        if len(bom_count) > 1:
            return {
                "name": _("BoM"),
                "type": "ir.actions.act_window",
                "res_model": "bill.material",
                "view_mode": "tree,form",
                "domain": [("id", "in", bom_count.ids)],
                "target": "current",
            }
        elif len(bom_count) == 1:
            return {
                "name": _("BoM"),
                "type": "ir.actions.act_window",
                "res_model": "bill.material",
                "res_id": bom_count.id,
                "view_mode": "form",
                "domain": [("id", "in", bom_count.ids)],
                "target": "current",
            }


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_bom_number = fields.Integer(string="Bill of Material", compute="_compute_product_bom_number")

    def _compute_product_bom_number(self):
        for rec in self:
            bom_count = self.env["bill.material"].search_count([("product_id.product_tmpl_id", "=", rec.id)])
            rec.product_bom_number = bom_count

    def action_view_bom(self):
        bom_count = self.env["bill.material"].search([("product_id.product_tmpl_id", "=", self.id)])
        if len(bom_count) > 1:
            return {
                "name": _("BoM"),
                "type": "ir.actions.act_window",
                "res_model": "bill.material",
                "view_mode": "tree,form",
                "domain": [("id", "in", bom_count.ids)],
                "target": "current",
            }
        elif len(bom_count) == 1:
            return {
                "name": _("BoM"),
                "type": "ir.actions.act_window",
                "res_model": "bill.material",
                "res_id": bom_count.id,
                "view_mode": "form",
                "domain": [("id", "in", bom_count.ids)],
                "target": "current",
            }
