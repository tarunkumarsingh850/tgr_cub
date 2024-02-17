import csv

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockFeed(models.Model):
    _name = "stock.feed"

    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company.id)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    product_brand_id = fields.Many2one("product.breeder", string="Product Brand")
    server_path = fields.Char(string="Server Path")
    filename = fields.Char("Filename")

    @api.constrains("warehouse_id", "product_brand_id")
    def _constrains_warehouse_product_brand(self):
        is_exists = self.env["stock.feed"].search(
            [
                ("id", "!=", self.id),
                ("warehouse_id", "=", self.warehouse_id.id),
                ("product_brand_id", "=", self.product_brand_id.id),
            ]
        )
        if is_exists:
            raise UserError(
                _(
                    f"Feed record with warehouse {self.warehouse_id.name} "
                    f"and brand {self.product_brand_id.breeder_name} already exists."
                )
            )

    @api.onchange("warehouse_id", "product_brand_id")
    def _onchange_warehouse_product_brand(self):
        if self.warehouse_id:
            if self.warehouse_id.dropshipping_code:
                code = "_" + self.warehouse_id.dropshipping_code
            else:
                code = ""
            warehouse_name = "_".join(self.warehouse_id.name.split(" "))
            brand_name = (
                ("_" + "_".join(self.product_brand_id.breeder_name.split(" "))) if self.product_brand_id else ""
            )
            filename = f"Stock_{warehouse_name}{code}{brand_name}.csv"
            self.filename = filename

    def stock_feed_csv_cron(self, **args):
        stock_feed_configs = self.env["stock.feed"].search([])
        for feed in stock_feed_configs:
            header_fields = ["SKU", "Quantity", "Brand", "Warehouse", "Warehouse Code"]
            data_rows = []
            domain = []
            if feed.product_brand_id:
                domain.append(("product_breeder_id", "=", feed.product_brand_id.id))
            product_ids = self.env["product.template"].sudo().search(domain)
            location = feed.warehouse_id.lot_stock_id
            for product in product_ids:
                product_t = self.env["product.product"].sudo().search([("product_tmpl_id", "=", product.id)], limit=1)
                stock = product_t.with_context(location=location.id).free_qty
                data_row = []
                data_row.append(product.default_code)
                data_row.append(stock)
                data_row.append(
                    feed.product_brand_id.breeder_name
                    if feed.product_brand_id
                    else product.product_breeder_id.breeder_name
                )
                data_row.append(feed.warehouse_id.name)
                data_row.append(feed.warehouse_id.dropshipping_code)
                data_rows.append(data_row)

            path = feed.server_path
            if path[-1] != "/":
                path += "/"
            path += feed.filename
            csvfile = open(path, "w")
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(header_fields)
            csvwriter.writerows(data_rows)
            csvfile.close()
