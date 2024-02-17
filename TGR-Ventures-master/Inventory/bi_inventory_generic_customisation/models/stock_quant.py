from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date, timedelta
import json
import requests
import logging

_logger = logging.getLogger(__name__)


class StockQuantFilter(models.Model):
    _inherit = "stock.quant"

    brand_id = fields.Many2one(
        "product.breeder", related="product_id.product_tmpl_id.product_breeder_id", string="Brand", store=True
    )
    flower_type_id = fields.Many2one(
        "flower.type", related="product_id.product_tmpl_id.flower_type_id", string="Flower Type Description"
    )
    product_sex_id = fields.Many2one(
        "product.sex", related="product_id.product_tmpl_id.product_sex_id", string="Sex Description"
    )
    supplier_sku_no = fields.Char(string="Supplier SKU", related="product_id.product_tmpl_id.supplier_sku_no")
    warehouse_stock_id = fields.Many2one("stock.warehouse", string="Warehouse", compute="_compute_warehouse_stock_id")
    product_cost = fields.Float(
        string="Product Cost", related="product_id.product_tmpl_id.standard_price", group_operator="avg"
    )
    product_sku = fields.Char(
        string="SKU",
        related="product_id.product_tmpl_id.default_code",
    )
    recently_created = fields.Boolean(
        string="Recently Created",
        related="product_id.product_tmpl_id.recently_created",
    )
    total_value = fields.Float(string="Total value", compute="compute_total_value")
    product_name = fields.Char(related="product_id.name", string="Product Name", store=True)
    total_counted_qty = fields.Float(string="Total Counted Quantity", compute="compute_total_counted_qty")
    apply_value = fields.Float(string="Apply Value", compute="_compute_apply_value", default=0.00)

    def _compute_warehouse_stock_id(self):
        for loacton in self:
            if loacton.location_id:
                warehouse = self.env["stock.warehouse"].search([("lot_stock_id", "=", loacton.location_id.id)])
                loacton.warehouse_stock_id = warehouse.id
            else:
                loacton.warehouse_stock_id = False

    @api.model
    def _get_inventory_fields_write(self):
        res = super(StockQuantFilter, self)._get_inventory_fields_write()
        res += ["brand_id", "flower_type_id", "product_sex_id", "supplier_sku_no", "warehouse_stock_id"]
        return res

    # scheduler function to update stock
    def update_uk_stock_cron(self):
        instance = self.env["magento.instance"].sudo().search([], limit=1)
        instance_url = instance.magento_url
        headers = self.get_headers(instance.access_token)
        m_product = self.env["magento.product.product"]
        product = self.env["product.product"]
        location_id = (
            self.env["stock.location"]
            .sudo()
            .search([("usage", "=", "internal"), ("magento_location", "in", ["uk_source"])], limit=1)
        )
        last_date = (instance.last_update_stock_time - timedelta(hours=2)) if instance.last_update_stock_time else False
        log_book = self.env["common.log.book.ept"].search([("is_data_import_log_book", "=", True)], limit=1)
        if not log_book:
            log_book = self.env["common.log.book.ept"].create({"is_data_import_log_book": True})
        if not last_date:
            last_date = date.today() - timedelta(days=1)
        product_ids = product.get_products_based_on_movement_date_ept(last_date, location_id.company_id)
        for location in location_id:
            magento_location = location.magento_location
            store_id = self.env["magento.storeview"].search([("location_id", "=", location.id)])
            if not store_id:
                raise UserError(_(f"{location.name} is not mapped to any store."))
            store_view_code = store_id.magento_storeview_code
            product_stock = m_product.get_magento_product_stock_ept(instance, product_ids, location.warehouse_id)
            api_url = f"{instance_url}/rest/{store_view_code}/async/bulk/V1/inventory/source-items"
            product_data = []
            p_name_log = []
            for p_id in product_stock.keys():
                p_record = product.browse(p_id)
                if p_record.default_code:
                    product_data.append(
                        {
                            "sku": p_record.default_code,
                            "source_code": magento_location,
                            "quantity": product_stock[p_id],
                            "status": 1,
                        }
                    )
                    p_name_log.append(p_record.default_code)
            count = 10000
            subsets = (product_data[x : x + count] for x in range(0, len(product_data), count))
            for subset in subsets:
                data = [{"sourceItems": subset}]
                response = requests.post(api_url, data=json.dumps(data), headers=headers)
                if response.status_code in [200, 202]:
                    instance.last_update_stock_time = fields.Datetime.now()
                log_book.write(
                    {
                        "log_lines": [
                            (
                                0,
                                0,
                                {
                                    "message": response.text,
                                    "api_url": api_url,
                                    "api_data_sent": json.dumps(data),
                                },
                            )
                        ]
                    }
                )

    def update_us_stock_cron(self):
        instance = self.env["magento.instance"].sudo().search([], limit=1)
        instance_url = instance.magento_url
        headers = self.get_headers(instance.access_token)
        m_product = self.env["magento.product.product"]
        product = self.env["product.product"]
        location_id = (
            self.env["stock.location"]
            .sudo()
            .search([("usage", "=", "internal"), ("magento_location", "in", ["usa_source"])], limit=1)
        )
        last_date = (instance.last_update_stock_time - timedelta(hours=2)) if instance.last_update_stock_time else False
        log_book = self.env["common.log.book.ept"].search([("is_data_import_log_book", "=", True)], limit=1)
        if not log_book:
            log_book = self.env["common.log.book.ept"].create({"is_data_import_log_book": True})
        if not last_date:
            last_date = date.today() - timedelta(days=1)
        product_ids = product.get_products_based_on_movement_date_ept(last_date, location_id.company_id)
        for location in location_id:
            magento_location = location.magento_location
            store_id = self.env["magento.storeview"].search([("location_id", "=", location.id)])
            if not store_id:
                raise UserError(_(f"{location.name} is not mapped to any store."))
            store_view_code = store_id.magento_storeview_code
            product_stock = m_product.get_magento_product_stock_ept(instance, product_ids, location.warehouse_id)
            api_url = f"{instance_url}/rest/{store_view_code}/async/bulk/V1/inventory/source-items"
            product_data = []
            p_name_log = []
            for p_id in product_stock.keys():
                p_record = product.browse(p_id)
                if p_record.default_code:
                    product_data.append(
                        {
                            "sku": p_record.default_code,
                            "source_code": magento_location,
                            "quantity": product_stock[p_id],
                            "status": 1,
                        }
                    )
                    p_name_log.append(p_record.default_code)
            count = 10000
            subsets = (product_data[x : x + count] for x in range(0, len(product_data), count))
            for subset in subsets:
                data = [{"sourceItems": subset}]
                response = requests.post(api_url, data=json.dumps(data), headers=headers)
                log_book.write(
                    {
                        "log_lines": [
                            (
                                0,
                                0,
                                {
                                    "message": response.text,
                                    "api_url": api_url,
                                    "api_data_sent": json.dumps(data),
                                },
                            )
                        ]
                    }
                )

    def update_eu_stock_cron(self):
        instance = self.env["magento.instance"].sudo().search([], limit=1)
        instance_url = instance.magento_url
        headers = self.get_headers(instance.access_token)
        m_product = self.env["magento.product.product"]
        product = self.env["product.product"]
        location_id = (
            self.env["stock.location"]
            .sudo()
            .search([("usage", "=", "internal"), ("magento_location", "in", ["eu_source"])], limit=1)
        )
        last_date = (instance.last_update_stock_time - timedelta(hours=2)) if instance.last_update_stock_time else False
        log_book = self.env["common.log.book.ept"].search([("is_data_import_log_book", "=", True)], limit=1)
        if not log_book:
            log_book = self.env["common.log.book.ept"].create({"is_data_import_log_book": True})
        if not last_date:
            last_date = date.today() - timedelta(days=1)
        product_ids = product.get_products_based_on_movement_date_ept(last_date, location_id.company_id)
        for location in location_id:
            magento_location = location.magento_location
            store_id = self.env["magento.storeview"].search([("location_id", "=", location.id)])
            if not store_id:
                raise UserError(_(f"{location.name} is not mapped to any store."))
            store_view_code = store_id.magento_storeview_code
            product_stock = m_product.get_magento_product_stock_ept(instance, product_ids, location.warehouse_id)
            api_url = f"{instance_url}/rest/{store_view_code}/async/bulk/V1/inventory/source-items"
            product_data = []
            p_name_log = []
            for p_id in product_stock.keys():
                p_record = product.browse(p_id)
                if p_record.default_code:
                    product_data.append(
                        {
                            "sku": p_record.default_code,
                            "source_code": magento_location,
                            "quantity": product_stock[p_id],
                            "status": 1,
                        }
                    )
                    p_name_log.append(p_record.default_code)
            count = 10000
            subsets = (product_data[x : x + count] for x in range(0, len(product_data), count))
            for subset in subsets:
                data = [{"sourceItems": subset}]
                response = requests.post(api_url, data=json.dumps(data), headers=headers)
                log_book.write(
                    {
                        "log_lines": [
                            (
                                0,
                                0,
                                {
                                    "message": response.text,
                                    "api_url": api_url,
                                    "api_data_sent": json.dumps(data),
                                },
                            )
                        ]
                    }
                )

    def update_ws_stock_cron(self):
        instance = self.env["magento.instance"].sudo().search([], limit=1)
        instance_url = instance.magento_url
        headers = self.get_headers(instance.access_token)
        m_product = self.env["magento.product.product"]
        product = self.env["product.product"]
        last_date = (instance.last_update_stock_time - timedelta(hours=2)) if instance.last_update_stock_time else False
        log_book = self.env["common.log.book.ept"].search([("is_data_import_log_book", "=", True)], limit=1)
        if not log_book:
            log_book = self.env["common.log.book.ept"].create({"is_data_import_log_book": True})
        if not last_date:
            last_date = date.today() - timedelta(days=1)
        product_ids = product.get_products_based_on_movement_date_ept(last_date, instance.company_id)
        locations = self.env["stock.location"].search(
            [("usage", "=", "internal"), ("magento_location", "in", ["wholesale"])]
        )
        for location in locations:
            magento_location = location.magento_location
            store_id = self.env["magento.storeview"].search([("location_id", "=", location.id)])
            if not store_id:
                raise UserError(_(f"{location.name} is not mapped to any store."))
            store_view_code = store_id.magento_storeview_code
            product_stock = m_product.get_magento_product_stock_ept(instance, product_ids, location.warehouse_id)
            api_url = f"{instance_url}/rest/{store_view_code}/async/bulk/V1/inventory/source-items"
            product_data = []
            p_name_log = []
            for p_id in product_stock.keys():
                p_record = product.browse(p_id)
                if p_record.default_code:
                    product_data.append(
                        {
                            "sku": p_record.default_code,
                            "source_code": magento_location,
                            "quantity": product_stock[p_id],
                            "status": 1,
                        }
                    )
                    p_name_log.append(p_record.default_code)
            count = 10000
            subsets = (product_data[x : x + count] for x in range(0, len(product_data), count))
            for subset in subsets:
                data = [{"sourceItems": subset}]
                response = requests.post(api_url, data=json.dumps(data), headers=headers)
                log_book.write(
                    {
                        "log_lines": [
                            (
                                0,
                                0,
                                {
                                    "message": response.text,
                                    "api_url": api_url,
                                    "api_data_sent": json.dumps(data),
                                },
                            )
                        ]
                    }
                )

    def get_headers(self, token):
        return {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "My User Agent 1.0",
            "Authorization": "Bearer {}".format(token),
        }

    @api.depends("quantity", "product_cost")
    def compute_total_value(self):
        for line in self:
            if line.quantity and line.product_cost:
                line.total_value = line.quantity * line.product_cost
            else:
                line.total_value = 0.00

    @api.depends("product_cost", "inventory_quantity")
    def compute_total_counted_qty(self):
        for line in self:
            line.total_counted_qty = 0.0
            if line.product_cost and line.inventory_quantity:
                line.total_counted_qty = line.product_cost * line.inventory_quantity

    @api.depends("product_cost", "inventory_diff_quantity")
    def _compute_apply_value(self):
        for line in self:
            inventory_diff_quantity = line.inventory_quantity - line.quantity or 0.00
            if line.inventory_diff_quantity:
                if line.product_cost and inventory_diff_quantity:
                    line.apply_value = line.product_cost * line.inventory_diff_quantity
                else:
                    line.apply_value = 0.0
            else:
                line.apply_value = 0.0

    @api.model
    def _get_quants_action(self, domain=None, extend=False):
        res = super(StockQuantFilter, self)._get_quants_action()
        res["domain"] = [("quantity", ">=", 0.00)]
        return res
