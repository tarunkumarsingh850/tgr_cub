from odoo import _, fields, models
import csv


class ProductProduct(models.Model):
    _inherit = "product.product"

    standard_price = fields.Float(
        "Cost",
        company_dependent=True,
        groups="base.group_user",
        digits=(12, 3),
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the next unit that will leave the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""",
    )
    last_cost_2 = fields.Float(related='product_tmpl_id.last_cost_2')
    recently_created = fields.Boolean("Recently Created", related="product_tmpl_id.recently_created")
    expected_qty = fields.Float("Expected Qty", compute="compute_expected_qty")
    # stock_location_ids = fields.Many2many("stock.location",string="Location On Hand",compute="_compute_stock_location_ids",store=True)

    def get_stock_update_csv_file_transfer(self, **args):
        header_fields = ["SKU", "ESPQty", "GBRQty", "Manufacturer", "Price", "Item Class"]
        data_rows = []
        product_ids = (
            self.env["product.template"]
            .sudo()
            .search(
                [
                    ("eu_tiger_one_boolean", "=", True),
                    ("default_code", "not ilike", "FREE-"),
                    ("wholesale_price_value", ">", 0),
                    ("product_breeder_id", "!=", False),
                ]
            )
        )
        location = self.env["stock.location"].sudo()
        uk_location = location.search([("magento_location", "=", "uk_source")])
        eu_location = location.search([("magento_location", "=", "eu_source")])
        for product in product_ids:
            product = self.env["product.product"].sudo().search([("product_tmpl_id", "=", product.id)], limit=1)
            uk_stock = product.with_context(location=uk_location.id).free_qty
            eu_stock = product.with_context(location=eu_location.id).free_qty
            data_row = []
            data_row.append(product.default_code)
            data_row.append(eu_stock)
            data_row.append(uk_stock)
            data_row.append(product.product_tmpl_id.product_breeder_id.breeder_name)
            data_row.append(product.product_tmpl_id.wholesale_price_value)
            data_row.append(product.product_tmpl_id.categ_id.name)
            data_rows.append(data_row)

        filename = f"/opt/stock-feed.csv"
        csvfile = open(filename, "w")
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header_fields)
        csvwriter.writerows(data_rows)
        csvfile.close()

    def get_free_stock_update_csv_file_transfer(self, **args):
        header_fields = ["SKU", "ESPQty", "GBRQty", "Manufacturer", "Price", "Item Class"]
        data_rows = []
        product_ids = (
            self.env["product.template"]
            .sudo()
            .search(
                [
                    ("wholesale_price_value", "=", 0),
                    ("retail_default_price", "=", 0),
                    ("product_breeder_id", "!=", False),
                ]
            )
        )
        location = self.env["stock.location"].sudo()
        uk_location = location.search([("magento_location", "=", "uk_source")])
        eu_location = location.search([("magento_location", "=", "eu_source")])
        for product in product_ids:
            product = self.env["product.product"].sudo().search([("product_tmpl_id", "=", product.id)], limit=1)
            uk_stock = product.with_context(location=uk_location.id).free_qty
            eu_stock = product.with_context(location=eu_location.id).free_qty
            data_row = []
            data_row.append(product.default_code)
            data_row.append(eu_stock)
            data_row.append(uk_stock)
            data_row.append(product.product_tmpl_id.product_breeder_id.breeder_name)
            data_row.append(product.product_tmpl_id.wholesale_price_value)
            data_row.append(product.product_tmpl_id.categ_id.name)
            data_rows.append(data_row)

        filename = f"/opt/free-stock-feed.csv"
        csvfile = open(filename, "w")
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header_fields)
        csvwriter.writerows(data_rows)
        csvfile.close()

    def compute_expected_qty(self):
        """
        compute function for expected qty field.
        """
        purchase_line_obj = self.env["purchase.order.line"]
        for product in self:
            product.expected_qty = 0
            po_lines = purchase_line_obj.search(
                [
                    ("product_id", "in", product.ids),
                    ("qty_received", "=", 0),
                    ("product_qty", ">", 0),
                    ("order_id.state", "=", "purchase"),
                ]
            )
            if po_lines:
                product.expected_qty = sum((po_lines).mapped("product_qty"))

    def action_product_expected_qty(self):
        """
        action return expected qty view.
        """
        self.ensure_one()
        view = self.env.ref("bi_inventory_generic_customisation.purchase_order_line_tree_view").id
        purchase_line_obj = self.env["purchase.order.line"]
        po_lines = purchase_line_obj.search(
            [
                ("product_id", "in", self.ids),
                ("qty_received", "=", 0),
                ("product_qty", ">", 0),
                ("order_id.state", "=", "purchase"),
            ]
        )
        action = {
            "name": _("Expected Quantity"),
            "view_mode": "list,form",
            "res_model": "purchase.order.line",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", po_lines.ids)],
        }
        return action

    # @api.depends("qty_available")
    # def _compute_stock_location_ids(self):
    #     for rec in self:
    #         location_ids = rec.env["stock.quant"].search([("product_id",'=',rec.id)]).mapped("location_id")
    #         filtered_location_ids = location_ids.filtered(lambda l:l.usage=='internal')
    #         if filtered_location_ids:
    #             rec.stock_location_ids = [(6,0,filtered_location_ids.ids)]
    #         else:
    #             rec.stock_location_ids = ''
