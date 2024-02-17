import requests
import json
import logging

from odoo import models, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger("MagentoEPT")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        fields_to_check = [
            "retail_uk_price",
            "retail_us_price",
            "retail_default_price",
            "wholesale_us",
            "wholesale_za",
            "wholesale_uk",
            "retail_za_price",
            "wholesale_price_value",
            # 'za_price',
            # 'retail_special_price',
            # 'wholesale_special_price',
            # 'wholesale_special_us',
            # 'wholesale_special_za',
            # 'wholesale_special_uk',
            # 'retail_special_us',
            # 'retail_special_za',
            # 'retail_special_uk',
        ]

        available_fields = vals.keys()
        required_fields = list(set(list(available_fields)) & set(fields_to_check))
        for rec in self:
            hist_vals = {
                "product_id": rec.id,
                "date": fields.Datetime.now(),
                "user_id": self.env.user.id,
            }
            for rf in required_fields:
                rf_key = [rf]
                rf_val = [vals.get(rf)]
                hist_vals.update(dict(zip(rf_key, rf_val)))
            if required_fields:
                try:
                    pph = self.env["product.price.history"].create(hist_vals)
                except Exception as e:
                    _logger.error(e)

        # update price change in magento
        instance = self.env["magento.instance"].sudo().search([], limit=1)
        api_url = f"{instance.magento_url}/rest/V1/products/base-prices"
        # api_url = "https://staging.tiger-one.eu/rest/V1/products/base-prices"
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "My User Agent 1.0",
            "Authorization": "Bearer {}".format(instance.access_token),
        }
        log_book = self.env["common.log.book.ept"].search([], limit=1)
        if not log_book:
            log_book = self.env["common.log.book.ept"].create({})
        for rf in required_fields:
            data = False
            if rf == "retail_uk_price":
                website = self.env["magento.website"].search([("name", "=", "Seedsman UK")])
                data = {
                    "prices": [
                        {"price": vals.get(rf), "store_id": 5, "sku": self.default_code, "extension_attributes": {}}
                    ]
                }
            elif rf == "retail_us_price":
                website = self.env["magento.website"].search([("name", "=", "Seedsman USA")])
                data = {
                    "prices": [
                        {
                            "price": vals.get(rf),
                            "store_id": website.magento_website_id,
                            "sku": self.default_code,
                            "extension_attributes": {},
                        }
                    ]
                }
            elif rf == "retail_default_price":
                website = self.env["magento.website"].search([("name", "=", "Seedsman EU")])
                data = {
                    "prices": [
                        {
                            "price": vals.get(rf),
                            "store_id": website.magento_website_id,
                            "sku": self.default_code,
                            "extension_attributes": {},
                        }
                    ]
                }
            elif rf == "retail_uk_price":
                website2 = self.env["magento.website"].search([("name", "=", "Seedsman UK")])
                data = {
                    "prices": [
                        {
                            "price": vals.get(rf),
                            "store_id": website.magento_website_id,
                            "sku": self.default_code,
                            "extension_attributes": {},
                        }
                    ]
                }
            elif rf == "wholesale_us":
                website = self.env["magento.website"].search([("name", "=", "Tiger One USA")])
                data = {
                    "prices": [
                        {
                            "price": vals.get(rf),
                            "store_id": website.magento_website_id,
                            "sku": self.default_code,
                            "extension_attributes": {},
                        }
                    ]
                }
            elif rf == "wholesale_za":
                website = self.env["magento.website"].search([("name", "=", "Tiger One SA")])
                data = {
                    "prices": [
                        {
                            "price": vals.get(rf),
                            "store_id": website.magento_website_id,
                            "sku": self.default_code,
                            "extension_attributes": {},
                        }
                    ]
                }
            elif rf == "wholesale_price_value":
                website = self.env["magento.website"].search([("name", "=", "Tiger One UK")])
                website2 = self.env["magento.website"].search([("name", "=", "Tiger One EU")])
                data = {
                    "prices": [
                        {
                            "price": vals.get(rf),
                            "store_id": website.magento_website_id,
                            "sku": self.default_code,
                            "extension_attributes": {},
                        },
                        {
                            "price": vals.get(rf),
                            "store_id": website2.magento_website_id,
                            "sku": self.default_code,
                            "extension_attributes": {},
                        },
                    ]
                }
            elif rf == "retail_za_price":
                website = self.env["magento.website"].search([("name", "=", "Seedsman SA")])
                data = {
                    "prices": [
                        {
                            "price": vals.get(rf),
                            "store_id": website.magento_website_id,
                            "sku": self.default_code,
                            "extension_attributes": {},
                        }
                    ]
                }
            if data:
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
                if response.status_code not in [200, 202]:
                    raise ValidationError(response.text)
                else:
                    pph.is_send_to_magento = True

        return super(ProductTemplate, self).write(vals)
