from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPArtner(models.Model):
    _inherit = "res.partner"

    discount_line_ids = fields.One2many(
        string="Discount Line",
        comodel_name="dropshipping.product.discount.line",
        inverse_name="partner_id",
    )
    global_discount_line_ids = fields.One2many(
        string="Global Discount Line",
        comodel_name="dropshipping.global.discount.line",
        inverse_name="partner_id",
    )


class DropshippingProductDiscountLine(models.Model):
    _name = "dropshipping.product.discount.line"
    _description = "Dropshipping Product Discount Line"

    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
    )
    brand_ids = fields.Many2many(
        string="Brand",
        comodel_name="product.breeder",
    )
    product_ids = fields.Many2many(
        string="Product",
        comodel_name="product.template",
    )
    percentage = fields.Float(
        string="Percentage",
    )


class DropshippingGlobalDiscountLine(models.Model):
    _name = "dropshipping.global.discount.line"
    _description = "Dropshipping global Discount Line"

    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
    )
    order_sku_count = fields.Selection(
        string="Order SKU Count",
        selection=[("25", "1-25"), ("50", "26-50"), ("75", "51-75"), ("100", "76-100"), ("100+", "100+")],
    )
    brand_ids = fields.Many2many(
        string="Brand",
        comodel_name="product.breeder",
    )

    sale_amount = fields.Float(
        string="Sale Amount",
    )

    percentage = fields.Float(
        string="Percentage",
    )

    @api.constrains("order_sku_count")
    def _check_order_sku_count(self):
        for record in self:
            is_exists = self.search(
                [
                    ("id", "!=", record.id),
                    ("partner_id", "=", record.partner_id.id),
                    ("order_sku_count", "=", record.order_sku_count),
                ]
            )
            if is_exists:
                value = dict(self._fields["order_sku_count"].selection).get(record.order_sku_count)
                raise UserError(_(f"You have already used {value} for {record.partner_id.name}."))
