from odoo import models, fields
from odoo.http import request
import json
import logging
import requests
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class UpdatePriceQuantity(models.TransientModel):
    _name = "update.price.wizard"
    _description = "Update Stock Price Wizard"

    magento_website_id = fields.Many2one("magento.website", string="Magento Website")
    brand_ids = fields.Many2many(
        string="Brand",
        comodel_name="product.breeder",
    )

    def update_price(self):

        instance = request.env["magento.instance"].sudo().search([], limit=1)
        api_url = instance.magento_price_update_url
        headers = self.get_headers(instance.access_token)
        domain = []
        if self.brand_ids:
            domain.append(("product_breeder_id", "in", self.brand_ids.ids))
        products = self.env["product.template"].search(domain)
        # products = self.env["product.product"].search([])
        for line in products:
            data = False
            if self.magento_website_id.name == "Tiger One UK":
                data = {
                    "prices": [
                        {
                            "price": line.wholesale_price_value,
                            "store_id": self.magento_website_id.magento_website_id,
                            "sku": line.default_code,
                            "extension_attributes": {},
                        }
                    ]
                }
            elif self.magento_website_id.name == "Tiger One EU":
                data = {
                    "prices": [
                        {
                            "price": line.wholesale_price_value,
                            "store_id": self.magento_website_id.magento_website_id,
                            "sku": line.default_code,
                            "extension_attributes": {},
                        }
                    ]
                }
            elif self.magento_website_id.name == "Tiger One USA":
                data = {
                    "prices": [
                        {
                            "price": line.wholesale_us,
                            "store_id": self.magento_website_id.magento_website_id,
                            "sku": line.default_code,
                            "extension_attributes": {},
                        }
                    ]
                }
            elif self.magento_website_id.name == "Wholesale":
                data = {
                    "prices": [
                        {
                            "price": line.wholesale_price_value,
                            "store_id": self.magento_website_id.magento_website_id,
                            "sku": line.default_code,
                            "extension_attributes": {},
                        }
                    ]
                }
            elif self.magento_website_id.name == "Seedsman EU":
                data = {
                    "prices": [
                        {
                            "price": line.retail_default_price,
                            "store_id": self.magento_website_id.magento_website_id,
                            "sku": line.default_code,
                            "extension_attributes": {},
                        }
                    ]
                }
            elif self.magento_website_id.name == "Seedsman UK":
                data = {
                    "prices": [
                        {
                            "price": line.retail_uk_price,
                            "store_id": self.magento_website_id.magento_website_id,
                            "sku": line.default_code,
                            "extension_attributes": {},
                        }
                    ]
                }
            elif self.magento_website_id.name == "Seedsman USA":
                data = {
                    "prices": [
                        {
                            "price": line.retail_us_price,
                            "store_id": self.magento_website_id.magento_website_id,
                            "sku": line.default_code,
                            "extension_attributes": {},
                        }
                    ]
                }
            if data:
                response = requests.post(api_url, data=json.dumps(data), headers=headers)
                if response.status_code in [200, 202]:
                    _logger.info(">>> successfully %s" % line.name)
                else:
                    raise ValidationError(response.content)
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
