from odoo import models, fields
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class UpdateProductDisable(models.TransientModel):
    _name = "update.product.disable"
    _description = "Update Product Disable"

    magento_storeview_id = fields.Many2many(string="Magento Storeview", comodel_name="magento.storeview")

    brand_ids = fields.Many2many(
        string="Brand",
        comodel_name="product.breeder",
    )

    def update_product_disable(self):

        instance = request.env["magento.instance"].sudo().search([], limit=1)
        instance_url = instance.magento_url
        instance_access_token = instance.access_token
        self.get_headers(f"{instance_access_token}")
        domain = [("magento_sku", "!=", False)]
        if self.brand_ids:
            domain.append(("brand_id", "in", self.brand_ids.ids))
        products = self.env["magento.product.configurable"].search(domain)
        status = 1
        data = []
        # api_url = f"https://www.tiger-one.eu/rest/{self.magento_storeview_id.magento_storeview_code}/async/bulk/V1/products/"
        for each in self.magento_storeview_id:
            api_url = f"{instance_url}/rest/{each.magento_storeview_code}/async/bulk/V1/products/"
            for line in products:
                if each.magento_storeview_code == "tigerone_uk_store_view":
                    status = 1 if line.uk_tiger_one_boolean else 2
                elif each.magento_storeview_code == "tigerone_eu_store_view":
                    status = 1 if line.eu_tiger_one_boolean else 2
                elif each.magento_storeview_code == "tigerone_sa_store_view":
                    status = 1 if line.sa_tiger_one_boolean else 2
                elif each.magento_storeview_code == "tigerone_us_store_view":
                    status = 1 if line.usa_tiger_one_boolean else 2
                elif each.magento_storeview_code == "uk":
                    status = 1 if line.uk_seedsman_boolean else 2
                elif each.magento_storeview_code == "us":
                    status = 1 if line.usa_seedsman_boolean else 2
                elif each.magento_storeview_code == "eu":
                    status = 1 if line.eu_seedsman_boolean else 2
                elif each.magento_storeview_code == "za":
                    status = 1 if line.sa_seedsman_boolean else 2
                elif each.magento_storeview_code == "eztestkits_uk_store_view":
                    status = 1 if line.uk_eztestkits_boolean else 2
                elif each.magento_storeview_code == "eztestkits_eu_store_view":
                    status = 1 if line.eu_eztestkits_boolean else 2
                elif each.magento_storeview_code == "eztestkits_sa_store_view":
                    status = 1 if line.sa_eztestkits_boolean else 2
                elif each.magento_storeview_code == "eztestkits_usa_store_view":
                    status = 1 if line.usa_eztestkits_boolean else 2
                elif each.magento_storeview_code == "pytho_nation_store_view":
                    status = 1 if line.pytho_n_boolean else 2
                data.append(
                    {
                        "product": {
                            "sku": line.magento_sku,
                            "status": status,
                        }
                    }
                )

            log_book = self.env["common.log.book.ept"].search([("is_data_import_log_book", "=", True)], limit=1)
            if not log_book:
                log_book = self.env["common.log.book.ept"].create({"is_data_import_log_book": True})
            count = 10000
            subsets = (data[x : x + count] for x in range(0, len(data), count))
            for subset in subsets:
                # response = requests.post(api_url, data=json.dumps(subset), headers=headers)
                log_book.write(
                    {
                        "log_lines": [
                            (
                                0,
                                0,
                                {
                                    # "message": response.text,
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

    def update_product_template_enable(self):
        instance = request.env["magento.instance"].sudo().search([], limit=1)
        instance_url = instance.magento_url
        instance_access_token = instance.access_token
        self.get_headers(f"{instance_access_token}")
        domain = []
        domain = [("default_code", "!=", False)]
        if self.brand_ids:
            domain.append(("product_breeder_id", "in", self.brand_ids.ids))
        products = self.env["product.template"].search(domain)
        status = 1
        data = []
        for each in self.magento_storeview_id:
            for line in products:
                if each.magento_storeview_code == "tigerone_uk_store_view":
                    status = 1 if line.uk_tiger_one_boolean else 2
                elif each.magento_storeview_code == "tigerone_eu_store_view":
                    status = 1 if line.eu_tiger_one_boolean else 2
                elif each.magento_storeview_code == "tigerone_sa_store_view":
                    status = 1 if line.sa_tiger_one_boolean else 2
                elif each.magento_storeview_code == "tigerone_us_store_view":
                    status = 1 if line.usa_tiger_one_boolean else 2
                elif each.magento_storeview_code == "uk":
                    status = 1 if line.uk_seedsman_boolean else 2
                elif each.magento_storeview_code == "us":
                    status = 1 if line.usa_seedsman_boolean else 2
                elif each.magento_storeview_code == "eu":
                    status = 1 if line.eu_seedsman_boolean else 2
                elif each.magento_storeview_code == "za":
                    status = 1 if line.sa_seedsman_boolean else 2
                elif each.magento_storeview_code == "eztestkits_uk_store_view":
                    status = 1 if line.uk_eztestkits_boolean else 2
                elif each.magento_storeview_code == "eztestkits_eu_store_view":
                    status = 1 if line.eu_eztestkits_boolean else 2
                elif each.magento_storeview_code == "eztestkits_sa_store_view":
                    status = 1 if line.sa_eztestkits_boolean else 2
                elif each.magento_storeview_code == "eztestkits_usa_store_view":
                    status = 1 if line.usa_eztestkits_boolean else 2
                elif each.magento_storeview_code == "pytho_nation_store_view":
                    status = 1 if line.pytho_n_boolean else 2
                data.append(
                    {
                        "product": {
                            "sku": line.default_code,
                            "status": status,
                        }
                    }
                )
            log_book = self.env["common.log.book.ept"].search([("is_data_import_log_book", "=", True)], limit=1)
            if not log_book:
                log_book = self.env["common.log.book.ept"].create({"is_data_import_log_book": True})
            api_url = f"{instance_url}/rest/{each.magento_storeview_code}/async/bulk/V1/products/"
            count = 10000
            subsets = (data[x : x + count] for x in range(0, len(data), count))
            for subset in subsets:
                # response = requests.post(api_url, data=json.dumps(subset), headers=headers)
                log_book.write(
                    {
                        "log_lines": [
                            (
                                0,
                                0,
                                {
                                    # "message": response.text,
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
