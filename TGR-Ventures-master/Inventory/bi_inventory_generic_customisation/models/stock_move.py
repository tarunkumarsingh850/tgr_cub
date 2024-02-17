from odoo import fields, api, models, _
from odoo.exceptions import UserError
from collections import defaultdict
from odoo.tools import float_is_zero, OrderedSet


class StockMoveReport(models.Model):
    _inherit = "stock.move"

    brand_id = fields.Many2one(
        "product.breeder", string="Brand", related="product_id.product_tmpl_id.product_breeder_id"
    )
    stock_onhand_quantity = fields.Float("Available Quantity", compute="_compute_stock_onhand_quantity")
    sales_price = fields.Float(string="Sales Price")
    cost = fields.Float(string="Cost", related="product_id.standard_price")
    total_cost = fields.Float("Total Cost", compute="compute_move_total_cost")
    product_sku = fields.Char("SKU", related="product_id.default_code")

    def action_trigger_sales_price(self):
        for record in self:
            if record.sale_line_id:
                record.sales_price = record.sale_line_id.price_subtotal

    def _compute_stock_onhand_quantity(self):
        for line in self:
            product_qty = line.product_id.with_context({"location": line.location_id.id}).free_qty
            line.stock_onhand_quantity = product_qty

    @api.ondelete(at_uninstall=False)
    def _unlink_if_draft_or_cancel(self):
        if any(move.state not in ("draft", "confirmed", "cancel") for move in self):
            raise UserError(_("You can only delete draft moves."))

    @api.depends("product_uom_qty", "cost")
    def compute_move_total_cost(self):
        for rec in self:
            if rec.product_uom_qty and rec.cost:
                rec.total_cost = rec.product_uom_qty * rec.cost
            else:
                rec.total_cost = 0.00

    def write(self, vals):
        for move in self:
            if (
                "picking_id" in vals
                and not vals.get("picking_id")
                and move.forecast_availability < 0
                and move.picking_id
            ):
                existing_note = move.picking_id.email_notification_content or ""
                note = "Product: {} is not available, So we credited {} amount.".format(
                    move.product_id.name,
                    format(move.sales_price * move.product_uom_qty, ".2f"),
                )
                move.picking_id.write(
                    {"email_notification_content": existing_note + "\n" + note, "is_send_email_notification": True}
                )
                move.picking_id.message_post(body=note)
        return super(StockMoveReport, self).write(vals)
    


    # def product_price_update_before_done(self, forced_qty=None):
    #     tmpl_dict = defaultdict(lambda: 0.0)
    #     # adapt standard price on incomming moves if the product cost_method is 'average'
    #     std_price_update = {}
    #     purchase_product_id = self.picking_id.purchase_id.order_line.filtered(lambda p: p.is_not_update_cost==True).mapped('product_id').ids
    #     for rec in self:
    #         if rec.product_id.id not in purchase_product_id:
    #             for move in rec.filtered(lambda move: move._is_in() and move.with_company(move.company_id).product_id.cost_method == 'average'):
    #                 product_tot_qty_available = move.product_id.sudo().with_company(move.company_id).quantity_svl + tmpl_dict[move.product_id.id]
    #                 rounding = move.product_id.uom_id.rounding

    #                 valued_move_lines = move._get_in_move_lines()
    #                 qty_done = 0
    #                 for valued_move_line in valued_move_lines:
    #                     qty_done += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)

    #                 qty = forced_qty or qty_done
    #                 if float_is_zero(product_tot_qty_available, precision_rounding=rounding):
    #                     new_std_price = move._get_price_unit()
    #                 elif float_is_zero(product_tot_qty_available + move.product_qty, precision_rounding=rounding) or \
    #                         float_is_zero(product_tot_qty_available + qty, precision_rounding=rounding):
    #                     new_std_price = move._get_price_unit()
    #                 else:
    #                     # Get the standard price
    #                     amount_unit = std_price_update.get((move.company_id.id, move.product_id.id)) or move.product_id.with_company(move.company_id).standard_price
    #                     new_std_price = ((amount_unit * product_tot_qty_available) + (move._get_price_unit() * qty)) / (product_tot_qty_available + qty)

    #                 tmpl_dict[move.product_id.id] += qty_done
    #                 # Write the standard price, as SUPERUSER_ID because a warehouse manager may not have the right to write on products
    #                 move.product_id.with_company(move.company_id.id).with_context(disable_auto_svl=True).sudo().write({'standard_price': new_std_price})
    #                 std_price_update[move.company_id.id, move.product_id.id] = new_std_price

    #             # adapt standard price on incomming moves if the product cost_method is 'fifo'
    #             for move in rec.filtered(lambda move:
    #                                     move.with_company(move.company_id).product_id.cost_method == 'fifo'
    #                                     and float_is_zero(move.product_id.sudo().quantity_svl, precision_rounding=move.product_id.uom_id.rounding)):
    #                 move.product_id.with_company(move.company_id.id).sudo().write({'standard_price': move._get_price_unit()})
