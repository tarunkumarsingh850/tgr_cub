from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BoM(models.Model):
    _name = "bill.material"
    _description = "Bill of Material"
    _rec_name = "product_id"

    product_id = fields.Many2one("product.product", string="Product")
    quantity = fields.Float("Quantity")
    uom_id = fields.Many2one("uom.uom", string="Unit")
    reference = fields.Char("Reference")
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company.id)
    bom_line_ids = fields.One2many("bill.material.line", "bill_material_id")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approve", "Approve"),
            ("done", "Done"),
        ],
        string="State",
    )

    def action_approve(self):
        self.state = "approve"

    def action_done(self):
        self.state = "done"

    @api.model
    def create(self, vals):
        res = super(BoM, self).create(vals)
        for rec in res:
            rec.state = "draft"
        return res

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            if self.product_id.uom_id:
                self.uom_id = self.product_id.uom_id.id

    def unlink(self):
        for each in self:
            if each.state == "done":
                raise UserError(_("You cannot delete this Record."))
        return super(BoM, self).unlink()


class BoMLine(models.Model):
    _name = "bill.material.line"
    _description = "Bill of Material Lines"

    bill_material_id = fields.Many2one("bill.material", string="bill_material_id")
    product_id = fields.Many2one("product.product", string="Product")
    line_quantity = fields.Float("Quantity")
    line_uom_id = fields.Many2one("uom.uom", string="Unit")
    is_no_track = fields.Boolean("is_no_track", default=False, copy=False)

    @api.onchange("product_id")
    def _onchange_product_id_uom(self):
        for each in self:
            if each.product_id:
                if each.product_id.uom_id:
                    each.line_uom_id = each.product_id.uom_id.id
            if each.product_id.tracking == "none":
                each.is_no_track = True
