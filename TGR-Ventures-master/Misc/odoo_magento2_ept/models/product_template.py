# See LICENSE file for full copyright and licensing details.
"""
Describes fields mapping to Magento products templates
"""
from odoo import models, fields
import json
import requests


class ProductTemplate(models.Model):
    """
    Describes fields mapping to Magento products templates
    """

    _inherit = "product.template"

    def _compute_magento_template_count(self):
        """
        calculate magento product template
        :return:
        """
        magento_template_obj = self.env["magento.product.template"]
        for product in self:
            magento_products = magento_template_obj.search([("odoo_product_template_id", "=", product.id)])
            product.magento_template_count = len(magento_products) if magento_products else 0

    magento_template_count = fields.Integer(string="# Product Count", compute="_compute_magento_template_count")
    magento_product_template_ids = fields.One2many(
        comodel_name="magento.product.template",
        inverse_name="odoo_product_template_id",
        string="Magento Products Templates",
        help="Magento Product Template Ids",
    )
    product_visibility = fields.Selection(
        string="Product Visibility",
        selection=[("1", "Not visible individually"), ("2", "Catalog"), ("3", "Search"), ("4", "Catalog,Search")],
    )

    def write(self, vals):
        """
        This method will archive/unarchive Magento product template based on Odoo Product template
        :param vals: Dictionary of Values
        """
        if "active" in vals.keys():
            m_template = self.env["magento.product.template"]
            for template in self:
                magento_templates = m_template.search([("odoo_product_template_id", "=", template.id)])
                if vals.get("active"):
                    magento_templates = m_template.search(
                        [("odoo_product_template_id", "=", template.id), ("active", "=", False)]
                    )
                magento_templates and magento_templates.write({"active": vals.get("active")})
        res = super(ProductTemplate, self).write(vals)
        return res

    def action_product_update_api(self):
        instance = self.env["magento.instance"].search([], limit=1)
        products = self.search([("create_date", ">=", instance.last_config_product_update_date)])
        log_book = self.env["common.log.book.ept"].search([], limit=1)
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "My User Agent 1.0",
            "Authorization": f"Bearer {instance.access_token}",
        }
        for product in products:
            product_data = {
                "product": {
                    "sku": product.default_code,
                    "name": product.name,
                    "attribute_set_id": int(product.categ_id.set_id),
                    "status": 1,
                    "visibility": int(product.product_visibility),
                    "type_id": "simple",
                    "price": product.wholesale_price_value,
                    "weight": product.weight,
                    "custom_attributes": [
                        {"attribute_code": "description", "value": product.description},
                        {"attribute_code": "brand", "value": product.product_breeder_id.magento_id},
                    ],
                }
            }
            api = f"{instance.magento_url}/rest/V1/products"
            response = requests.post(api, data=json.dumps(product_data), headers=headers)
            log_book.write(
                {
                    "log_lines": [
                        (
                            0,
                            0,
                            {
                                "message": response.text,
                                "api_url": api,
                                "api_data_sent": json.dumps(product_data),
                            },
                        )
                    ]
                }
            )
