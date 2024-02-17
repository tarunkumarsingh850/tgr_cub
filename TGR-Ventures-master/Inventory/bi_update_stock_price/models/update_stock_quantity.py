from odoo import models, fields, _
from odoo.http import request
import json
import logging
import requests
from odoo.exceptions import UserError
from datetime import date, timedelta

_logger = logging.getLogger(__name__)


class UpdateStockQuantity(models.TransientModel):
    _name = "update.quantity.wizard"
    _description = "Update Stock Quantity Wizard"

    magento_location_id = fields.Many2one("magento.inventory.locations", string="Magento Location")

    # product_id = fields.Many2one(
    #     string='Product',
    #     comodel_name='product.product',
    # )

    brand_ids = fields.Many2many(
        string="Brand",
        comodel_name="product.breeder",
    )

    def update_quantity(self):
        instance = request.env["magento.instance"].sudo().search([], limit=1)
        instance_url = instance.magento_url
        headers = self.get_headers(instance.access_token)
        m_product = self.env["magento.product.product"]
        product = self.env["product.product"]
        last_date = instance.last_update_stock_time
        log_book = self.env["common.log.book.ept"].search([("is_data_import_log_book", "=", True)], limit=1)
        if not log_book:
            log_book = self.env["common.log.book.ept"].create({"is_data_import_log_book": True})
        if not last_date:
            last_date = date.today() - timedelta(days=1)
        product_ids = product.get_products_based_on_movement_date_ept(last_date, instance.company_id)
        if self.brand_ids:
            product_ids = (
                self.env["product.product"]
                .search([("id", "in", product_ids), ("product_tmpl_id.product_breeder_id", "in", self.brand_ids.ids)])
                .ids
            )

        locations = self.env["stock.location"].search(
            [("usage", "=", "internal"), ("magento_location", "=", self.magento_location_id.magento_location_code)]
        )
        for location in locations:
            magento_location = location.magento_location
            store_id = self.env["magento.storeview"].search([("location_id", "=", location.id)])
            if not store_id:
                raise UserError(_(f"{self.magento_location_id.name} store has no inventory location specified."))
            store_view_code = store_id.magento_storeview_code
            if location.magento_location == "sm_usa_source":
                product_stock = self.env["product.product"].get_onhand_qty_ept(location.warehouse_id, product_ids)
            else:
                product_stock = m_product.get_magento_product_stock_ept(instance, product_ids, location.warehouse_id)
            api_url = f"{instance_url}/rest/{store_view_code}/async/bulk/V1/inventory/source-items"
            product_data = []
            p_name_log = []
            for p_id in product_stock.keys():
                p_record = product.browse(p_id)
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
        return {
            "effect": {
                "fadeout": "slow",
                "message": " Updated Successfully!",
                "img_url": "/web/static/src/img/smile.svg",
                "type": "rainbow_man",
            }
        }

    def get_headers(self, token):
        return {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "My User Agent 1.0",
            "Authorization": "Bearer {}".format(token),
        }

    def export_stock_data(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {},
        }
        return self.env.ref("bi_update_stock_price.action_update_stock_data_export").report_action(
            self, data=data, config=False
        )
