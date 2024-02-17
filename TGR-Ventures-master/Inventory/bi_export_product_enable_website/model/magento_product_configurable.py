import requests
import json
from odoo.exceptions import UserError
from odoo import models, fields, _, api
from odoo.http import request
from datetime import timedelta


class MagentoProductConfigurable(models.Model):
    _name = "magento.product.configurable"
    _rec_name = "magento_sku"

    magento_product_id = fields.Char("Magento Product ID")
    magento_product_name = fields.Char("Magento Product Name")
    magento_product_type = fields.Char("Magento Product Type")
    magento_sku = fields.Char(string="Magento Product SKU", help="Magento Product SKU")
    product_type = fields.Char(string="Product Type(class)")
    uk_tiger_one_boolean = fields.Boolean(string="UK Tiger One Enable/Disable", default=True)
    eu_tiger_one_boolean = fields.Boolean(string="EU Tiger One Enable/Disable", default=True)
    sa_tiger_one_boolean = fields.Boolean(string="SA Tiger One Enable/Disable", default=True)
    usa_tiger_one_boolean = fields.Boolean(string="USA Tiger One Enable/Disable", default=True)
    uk_seedsman_boolean = fields.Boolean(string="UK Seedsman Enable/Disable", default=True)
    eu_seedsman_boolean = fields.Boolean(string="EU Seedsman Enable/Disable", default=True)
    sa_seedsman_boolean = fields.Boolean(string="SA Seedsman Enable/Disable", default=True)
    usa_seedsman_boolean = fields.Boolean(string="USA Seedsman Enable/Disable", default=True)
    uk_eztestkits_boolean = fields.Boolean(string="UK Eztestkits Enable/Disable", default=True)
    eu_eztestkits_boolean = fields.Boolean(string="EU Eztestkits Enable/Disable", default=True)
    sa_eztestkits_boolean = fields.Boolean(string="SA Eztestkits Enable/Disable", default=True)
    usa_eztestkits_boolean = fields.Boolean(string="USA Eztestkits Enable/Disable", default=True)
    pytho_n_boolean = fields.Boolean(string="Pytho N Enable/Disable", default=True)
    categ_id = fields.Many2one(
        string="Category",
        comodel_name="product.category",
    )
    description = fields.Char(
        string="Description",
    )
    product_visibility = fields.Selection(
        string="Product Visibility",
        selection=[("1", "Not visible individually"), ("2", "Catalog"), ("3", "Search"), ("4", "Catalog,Search")],
    )
    brand_id = fields.Many2one(
        "product.breeder",
        string="Product Brand",
    )
    magento_attribute_ids = fields.One2many(
        string="Magento Attribute",
        comodel_name="product.magento.attribute",
        inverse_name="magento_product_config_id",
    )

    pack_size_ids = fields.Many2many(
        string="Pack Size",
        comodel_name="pack.size.configurable",
    )
    flower_type_id = fields.Many2one("flower.type", string="Flower Type Description")
    product_sex_id = fields.Many2one("product.sex", string="Sex Description")
    product_count = fields.Integer(string="Products", compute="_compute_product_count")
    product_ids = fields.Many2many(
        string="product",
        comodel_name="product.template",
    )

    def write(self, vals):
        fields_to_check = [
            "uk_tiger_one_boolean",
            "eu_tiger_one_boolean",
            "sa_tiger_one_boolean",
            "usa_tiger_one_boolean",
            "uk_seedsman_boolean",
            "eu_seedsman_boolean",
            "sa_seedsman_boolean",
            "usa_seedsman_boolean",
            "uk_eztestkits_boolean",
            "eu_eztestkits_boolean",
            "sa_eztestkits_boolean",
            "usa_eztestkits_boolean",
            "pytho_n_boolean",
        ]

        available_fields = vals.keys()
        required_fields = list(set(list(available_fields)) & set(fields_to_check))
        instance = self.env["magento.instance"].sudo().search([], limit=1)
        instance_url = instance.magento_url
        log_book = self.env["common.log.book.ept"].search([("is_data_import_log_book", "=", True)], limit=1)
        if not log_book:
            log_book = self.env["common.log.book.ept"].create({"is_data_import_log_book": True})
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "My User Agent 1.0",
            "Authorization": "Bearer {}".format(instance.access_token),
        }
        for rf in required_fields:

            store_code = False
            data = False

            if rf == "uk_tiger_one_boolean":
                store_code = "tigerone_uk_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.magento_sku,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "eu_tiger_one_boolean":
                store_code = "tigerone_eu_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.magento_sku,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "sa_tiger_one_boolean":
                store_code = "tigerone_sa_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.magento_sku,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "usa_tiger_one_boolean":
                store_code = "tigerone_us_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.magento_sku,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "uk_seedsman_boolean":
                store_code = "uk"
                data = [
                    {
                        "product": {
                            "sku": self.magento_sku,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "eu_seedsman_boolean":
                store_code = "eu"
                data = [
                    {
                        "product": {
                            "sku": self.magento_sku,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "sa_seedsman_boolean":
                store_code = "za"
                data = [
                    {
                        "product": {
                            "sku": self.magento_sku,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "usa_seedsman_boolean":
                store_code = "us"
                data = [
                    {
                        "product": {
                            "sku": self.magento_sku,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "uk_eztestkits_boolean":
                store_code = "eztestkits_uk_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.magento_sku,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "eu_eztestkits_boolean":
                store_code = "eztestkits_eu_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.magento_sku,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "sa_eztestkits_boolean":
                store_code = "eztestkits_sa_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.magento_sku,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "usa_eztestkits_boolean":
                store_code = "eztestkits_usa_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.magento_sku,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "pytho_n_boolean":
                store_code = "pytho_nation_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.magento_sku,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]

            if store_code and data:
                api_url = f"{instance_url}/rest/{store_code}/async/bulk/V1/products/"
                # api_url = f"https://staging.tiger-one.eu/rest/{store_code}/async/bulk/V1/products/"
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
        return super(MagentoProductConfigurable, self).write(vals)

    def action_create_product(self):
        for record in self:
            products_ids = []
            if record.pack_size_ids:
                for pack_size in record.pack_size_ids:
                    attributes = []
                    for attribute in record.magento_attribute_ids:

                        attributes.append(
                            (
                                0,
                                0,
                                {
                                    "attribute_id": attribute.attribute_id.id,
                                    "attribute_val_id": attribute.attribute_val_id.id,
                                },
                            )
                        )
                    if record.magento_sku:
                        sku = record.magento_sku + "-" + pack_size.code
                    else:
                        sku = pack_size.code
                    product_val = {
                        "name": record.magento_product_name,
                        "categ_id": record.categ_id.id if record.categ_id else False,
                        "product_breeder_id": record.brand_id.id if record.brand_id else False,
                        "detailed_type": "product",
                        "default_code": sku,
                        "uk_tiger_one_boolean": record.uk_tiger_one_boolean,
                        "eu_tiger_one_boolean": record.eu_tiger_one_boolean,
                        "sa_tiger_one_boolean": record.sa_tiger_one_boolean,
                        "usa_tiger_one_boolean": record.usa_tiger_one_boolean,
                        "usa_tiger_one_boolean": record.usa_tiger_one_boolean,
                        "eu_seedsman_boolean": record.eu_seedsman_boolean,
                        "sa_seedsman_boolean": record.sa_seedsman_boolean,
                        "usa_seedsman_boolean": record.usa_seedsman_boolean,
                        "uk_eztestkits_boolean": record.uk_eztestkits_boolean,
                        "eu_eztestkits_boolean": record.eu_eztestkits_boolean,
                        "sa_eztestkits_boolean": record.sa_eztestkits_boolean,
                        "usa_eztestkits_boolean": record.usa_eztestkits_boolean,
                        "pytho_n_boolean": record.pytho_n_boolean,
                        "pack_size_desc": pack_size.name,
                        "flower_type_id": record.flower_type_id.id,
                        "product_sex_id": record.product_sex_id.id,
                        "magento_attribute_ids": attributes,
                    }
                    product_id = self.env["product.template"].search(
                        [("name", "=", record.magento_product_name), ("default_code", "=", sku)]
                    )
                    if product_id:
                        raise UserError(_("Product already created."))
                    else:
                        product_id = self.env["product.template"].create(product_val)
                        products_ids.append(product_id.id)
                record.product_ids = [(6, 0, products_ids)]

    @api.depends("product_ids")
    def _compute_product_count(self):
        for record in self:
            product_count = 0
            if record.product_ids:
                for product in record.product_ids:
                    product_count += 1
            record.product_count = product_count

    def action_view_simple_products(self):
        if self.product_ids:
            return {
                "name": _("Products"),
                "view_type": "form",
                "view_mode": "tree,form",
                "res_model": "product.template",
                "view_id": False,
                "type": "ir.actions.act_window",
                "domain": [("id", "in", self.product_ids.ids)],
            }

    def unlink(self):
        for record in self:
            if record.product_ids:
                raise UserError(_("You cannot delete this Record."))
        return super(MagentoProductConfigurable, self).unlink()

    def action_config_product_update_api(self):
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
                    "sku": product.magento_sku,
                    "name": product.magento_product_name,
                    "attribute_set_id": int(product.categ_id.set_id),
                    "status": 1,
                    "visibility": int(product.product_visibility),
                    "type_id": "configurable",
                    "custom_attributes": [
                        {"attribute_code": "description", "value": product.description},
                        {"attribute_code": "brand", "value": product.brand_id.magento_id},
                    ],
                }
            }
            api = f"{instance.magento_url}/rest/V1/products"
            response = requests.post(api, data=json.dumps(product_data), headers=headers)
            if response.status_code in [200]:
                product.magento_product_id = json.loads(response.text).get("id", "")
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

    def configurable_product_enable_disable_cron(self):

        instance = request.env["magento.instance"].sudo().search([], limit=1)
        instance_url = instance.magento_url
        instance_access_token = instance.access_token
        headers = self.get_headers(f"{instance_access_token}")
        today_minus_20 = fields.Datetime.now() - timedelta(days=20)
        domain = [("magento_sku", "!=", False), ("write_date", ">", today_minus_20)]
        products = self.env["magento.product.configurable"].search(domain)
        status = 1
        data = []
        for each in instance.magento_website_ids.store_view_ids:
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
                response = requests.post(api_url, data=json.dumps(subset), headers=headers)
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


class ProductMagentoAttribte(models.Model):
    _inherit = "product.magento.attribute"

    magento_product_config_id = fields.Many2one(
        string="Magento Attribute",
        comodel_name="magento.product.configurable",
    )
