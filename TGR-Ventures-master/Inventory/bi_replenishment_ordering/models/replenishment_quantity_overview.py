from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReplenishmentQuantityOverview(models.Model):
    _name = "replenishment.quantity.overview"
    _description = "Replenishment Quantity Overview"
    _inherit = "mail.thread"
    _order = "date desc, name desc"

    name = fields.Char("Name", copy=False, default=lambda self: _("New"))
    date = fields.Date("Date", default=fields.Date.today(), copy=False)
    brand_id = fields.Many2one("product.breeder", string="Brand", copy=False, tracking=True)
    brand_ids = fields.Many2many("product.breeder", string="Brands", copy=False, tracking=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", copy=False, tracking=True)
    sex_id = fields.Many2one("product.sex", string="Sex", copy=False, tracking=True)
    flower_type_id = fields.Many2one("flower.type", string="Flower Type", copy=False, tracking=True)
    size_id = fields.Many2one("product.size", string="Size", copy=False, tracking=True)
    date_range = fields.Selection(
        [
            ("0.5", "15 days"),
            ("1", "30 days"),
            ("1.5", "45 days"),
            ("2", "60 days"),
            ("3", "90 days"),
            ("4", "120 days"),
        ],
        string="Date Range",
        tracking=True,
    )
    line_ids = fields.One2many("replenishment.quantity.overview.line", "overview_id", copy=False, tracking=True)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")], string="Status", default="draft", tracking=True
    )
    purchase_id = fields.Many2one("purchase.order", string="Purchase")
    order_count = fields.Integer("Orders", compute="_compute_orders")
    user_id = fields.Many2one("res.users", string="User", default=lambda self: self.env.user.id, tracking=True)

    def _compute_orders(self):
        for rec in self:
            order_ids = self.env["purchase.order"].search(
                [("replenishment_order_id", "=", self.id), ("state", "!=", "cancel")]
            )
            rec.order_count = len(order_ids)

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("replenishment.order.sequence")
        res = super(ReplenishmentQuantityOverview, self).create(vals)
        return res

    def unlink(self):
        if self.state == "confirmed":
            raise UserError(_("You cannot delete a replenishment order that is confirmed."))
        return super(ReplenishmentQuantityOverview, self).unlink()

    def load_lines(self):
        domain = []
        domain.append(("is_exclude_from_replenishment", "=", False))
        if self.flower_type_id:
            domain.append(("flower_type_id", "=", self.flower_type_id.id))
        if self.sex_id:
            domain.append(("product_sex_id", "=", self.sex_id.id))
        if self.size_id:
            domain.append(("product_size_id", "=", self.size_id))
        if self.brand_ids:
            domain.append(("product_breeder_id", "in", self.brand_ids.ids))
            domain.append(("product_breeder_id", "!=", False))
        product_ids = self.env["product.template"].search(domain)
        for product in product_ids:
            product_id = self.env["product.product"].search([("product_tmpl_id", "=", product.id)])
            total_delivered_quantity = 0
            start_period_date = date(fields.Date.today().year, 1, 1)
            end_period_date = fields.Date.today()
            months = (
                (end_period_date.year - start_period_date.year) * 12 + end_period_date.month - start_period_date.month
            )
            qty_delivered = 0
            sale_line_ids = self.env["sale.order.line"].search(
                [
                    ("product_id", "=", product_id.id),
                    ("order_id.state", "in", ("done", "sale")),
                    ("order_id.date_order", ">=", start_period_date),
                    ("order_id.date_order", "<=", end_period_date),
                ]
            )
            qty_delivered = sum(sale_line_ids.mapped("qty_delivered"))
            total_delivered_quantity += qty_delivered
            purchase_order_ids = self.env["purchase.order"].search(
                [
                    ("picking_type_id.default_location_dest_id", "=", self.warehouse_id.lot_stock_id.id),
                    ("is_created_picking", "=", False),
                    ("state", "in", ("done", "purchase")),
                ]
            )
            purchase_reserved_qty = sum(
                purchase_order_ids.mapped("order_line")
                .filtered(lambda line: line.product_id == product_id)
                .mapped("product_qty")
            )
            free_quantity = product_id.with_context({"location": self.warehouse_id.lot_stock_id.id}).free_qty
            avail_qty = free_quantity + purchase_reserved_qty
            supplier = product.seller_ids[0].name if product_id.seller_ids else False
            average = (total_delivered_quantity / months) if months else 0
            ideal_qty = round(average * float(self.date_range))
            order_qty = round((ideal_qty - free_quantity) - purchase_reserved_qty)
            if order_qty <= 0:
                order_qty = 0
            self.env["replenishment.quantity.overview.line"].create(
                {
                    "overview_id": self.id,
                    "product_id": product_id.id,
                    "supplier_id": supplier.id if supplier else False,
                    "on_order_quantity": purchase_reserved_qty,
                    "ideal_quantity": ideal_qty,
                    "available_quantity": avail_qty,
                    "suggested_reorder_quantity": order_qty,
                }
            )
        self.state = "confirmed"

    def view_lines(self):
        return {
            "name": _("Products"),
            "type": "ir.actions.act_window",
            "res_model": "replenishment.quantity.overview.line",
            "view_mode": "tree",
            "domain": [("overview_id", "=", self.id)],
        }

    def view_orders(self):
        order_ids = self.env["purchase.order"].search(
            [("replenishment_order_id", "=", self.id), ("state", "!=", "cancel")]
        )
        if len(order_ids) > 1:
            return {
                "name": _("Replenishment Purchase Orders"),
                "type": "ir.actions.act_window",
                "res_model": "purchase.order",
                "view_mode": "tree,form",
                "domain": [("id", "in", order_ids.ids)],
            }
        else:
            return {
                "name": _("Replenishment Purchase Orders"),
                "type": "ir.actions.act_window",
                "res_model": "purchase.order",
                "res_id": order_ids[0].id,
                "view_mode": "form",
            }


class ReplenishmentQuantityOverviewLines(models.Model):
    _name = "replenishment.quantity.overview.line"
    _description = "Replenishment Quantity Overview Lines"

    overview_id = fields.Many2one("replenishment.quantity.overview", ondelete="cascade")
    date = fields.Date("Date", related="overview_id.date")
    product_id = fields.Many2one("product.product", string="Product", copy=False)
    product_age = fields.Selection(
        [("new", "New"), ("old", "Old")], string="Product Age", compute="_compute_product_age"
    )
    supplier_id = fields.Many2one("res.partner", string="Supplier")
    last_year_order_quantity = fields.Float("Last Year Order Quantity", default=0)
    on_order_quantity = fields.Float("On Order Quantity")
    ideal_quantity = fields.Float("Ideal Quantity")
    available_quantity = fields.Float("Available Quantity")
    suggested_reorder_quantity = fields.Float("Order Quantity")

    def _compute_product_age(self):
        product_days = (
            self.env["ir.config_parameter"].sudo().get_param("bi_inventory_generic_customisation.product_days")
        )
        for line in self:
            if (fields.Datetime.now() - line.product_id.create_date).days < int(product_days):
                line.product_age = "new"
            else:
                line.product_age = "old"

    def create_order(self):
        overview = self.mapped("overview_id")
        orders = self.env["purchase.order"].search(
            [("replenishment_order_id", "in", overview.ids), ("state", "!=", "cancel")]
        )
        # if orders:
        #     raise UserError(_("You cannot create order for this replenishment. Orders already exist."))
        suppliers = self.mapped("supplier_id")
        new_orders = []
        for supplier in suppliers:
            lines = self.filtered(lambda l: l.supplier_id == supplier)
            order_lines = []
            for line in lines.filtered(lambda l2: l2.suggested_reorder_quantity > 0):
                order_line = {
                    "product_id": line.product_id.id,
                    "product_qty": line.suggested_reorder_quantity,
                }
                order_lines.append((0, 0, order_line))
            order_details = {
                "partner_id": supplier.id,
                "order_line": order_lines,
                "replenishment_order_id": overview.id,
            }
            purchase = self.env["purchase.order"].create(order_details)
            new_orders.append(purchase.id)
        if len(new_orders) > 1:
            return {
                "name": _("Replenishment Purchase Orders"),
                "type": "ir.actions.act_window",
                "res_model": "purchase.order",
                "view_mode": "tree,form",
                "domain": [("id", "in", new_orders)],
            }
        else:
            return {
                "name": _("Replenishment Purchase Orders"),
                "type": "ir.actions.act_window",
                "res_model": "purchase.order",
                "res_id": new_orders[0],
                "view_mode": "form",
            }
