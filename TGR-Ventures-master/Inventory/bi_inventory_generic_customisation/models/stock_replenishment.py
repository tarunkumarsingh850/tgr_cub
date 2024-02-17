from odoo import fields, models, api
import datetime


class StockReplenishment(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    check_color = fields.Boolean("check_color", compute="_compute_check_color", default=False)
    brand_id = fields.Many2one(
        "product.breeder", string="Brand", related="product_id.product_tmpl_id.product_breeder_id"
    )
    recently_created = fields.Boolean("field_name", default=False, copy=False)
    zero_onhand = fields.Boolean("field_name", default=False, copy=False)

    @api.depends("name")
    def _compute_check_color(self):
        for each in self:
            if each.qty_on_hand == 0:
                each.check_color = False
                each.zero_onhand = True
            product_days = (
                self.env["ir.config_parameter"].sudo().get_param("bi_inventory_generic_customisation.product_days")
            )

            date_created = each.create_date + datetime.timedelta(days=int(product_days))
            if date_created.date() >= datetime.datetime.now().date():
                each.check_color = True
                each.recently_created = True
            else:
                each.check_color = False
                each.recently_created = False
