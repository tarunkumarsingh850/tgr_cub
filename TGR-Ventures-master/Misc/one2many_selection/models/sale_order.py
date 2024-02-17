from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Demo method that will delete your sale orde line as you select and press delete
    @api.model
    def create_purchase_wizard(self, selected_ids):
        new = 1
        if new == 1:
            return {"error": True}
        orderline_sudo = self.env["sale.order.line"].sudo()
        order_lines = orderline_sudo.browse(selected_ids)
        order_id = order_lines.mapped("order_id")
        if order_id.state not in ("draft", "sent"):
            return False
        else:
            product_ids = []
            for line in order_lines:
                sale_id = line.order_id.id
                product_ids.append(
                    (
                        0,
                        0,
                        {
                            "product_id": line.product_id.id,
                            "description_name": line.name,
                            "quantity": line.product_uom_qty,
                            "unit_price": line.price_unit,
                            "price_subtotal": line.price_subtotal,
                            "sale_id": sale_id,
                        },
                    )
                )
            return {"line_ids": product_ids}
