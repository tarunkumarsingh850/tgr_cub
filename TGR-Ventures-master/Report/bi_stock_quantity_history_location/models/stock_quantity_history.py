from odoo import models, fields


class StockQuantityHistory(models.TransientModel):
    _inherit = "stock.quantity.history"

    location_ids = fields.Many2many("stock.location", string="Location", domain="[('usage', '=', 'internal')]")
    brand_id = fields.Many2one("product.breeder", string="Brand")
    warehouse_stock_id = fields.Many2one("stock.warehouse", string="Warehouse")

    # def open_at_date(self):
    #     active_model = self.env.context.get('active_model')
    #     if active_model == 'stock.valuation.layer':
    #         action = self.env["ir.actions.actions"]._for_xml_id("stock_account.stock_valuation_layer_action")
    #         if self.brand_id:
    #             action['domain'] = [('create_date', '<=', self.inventory_datetime),("product_tmpl_id.product_breeder_id", "=", self.brand_id.id),('product_id.type', '=', 'product')]
    #         else:
    #           action['domain'] = [('create_date', '<=', self.inventory_datetime),('product_id.type', '=', 'product')]
    #         action['display_name'] = format_datetime(self.env, self.inventory_datetime)
    #         if self.location_ids:
    #             action['context'] = dict(self.env.context, to_date=self.inventory_datetime,location = self.location_ids.ids)
    #         else:
    #             action['context'] = dict(self.env.context, to_date=self.inventory_datetime)
    #         return action
    #     return super(StockQuantityHistory, self).open_at_date()
