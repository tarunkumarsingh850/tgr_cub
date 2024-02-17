# See LICENSE file for full copyright and licensing details.
"""
Describes fields and methods for Magento products
"""
import logging
import json
from datetime import datetime
from odoo import fields, models, _
from odoo.exceptions import UserError
from .api_request import req, create_search_criteria
from ..python_library.php import Php

_logger = logging.getLogger("MagentoEPT")


class MagentoProductProduct(models.Model):
    """
    Describes fields and methods for Magento products
    """

    _name = "magento.product.product"
    _description = "Magento Product"
    _rec_name = "magento_product_name"

    magento_instance_id = fields.Many2one(
        comodel_name="magento.instance", string="Instance", help="This field relocates magento instance"
    )
    magento_product_id = fields.Char(string="Magento Product", help="Magento Product Id")
    magento_product_name = fields.Char(string="Magento Product Name", help="Magento Product Name", translate=True)
    magento_tmpl_id = fields.Many2one(
        comodel_name="magento.product.template",
        string="Magento Product template",
        help="Magento Product template",
        ondelete="cascade",
    )
    odoo_product_id = fields.Many2one(
        comodel_name="product.product", string="Odoo Product", required=True, ondelete="restrict", copy=False
    )
    magento_website_ids = fields.Many2many(
        comodel_name="magento.website",
        string="Magento Websites",
        readonly=False,
        domain="[('magento_instance_id','=',magento_instance_id)]",
        help="Magento Websites",
    )
    product_type = fields.Selection(
        [
            ("simple", "Simple Product"),
            ("configurable", "Configurable Product"),
            ("virtual", "Virtual Product"),
            ("downloadable", "Downloadable Product"),
            ("group", "Group Product"),
            ("bundle", "Bundle Product"),
        ],
        string="Magento Product Type",
        help="Magento Product Type",
        default="simple",
    )
    created_at = fields.Date(string="Product Created At", help="Date when product created into Magento")
    updated_at = fields.Date(string="Product Updated At", help="Date when product updated into Magento")

    magento_sku = fields.Char(string="Magento Product SKU", help="Magento Product SKU")
    description = fields.Text(string="Product Description", help="Description", translate=True)
    short_description = fields.Text(string="Product Short Description", help="Short Description", translate=True)
    magento_product_image_ids = fields.One2many(
        "magento.product.image", "magento_product_id", string="Magento Product Images", help="Magento Product Images"
    )
    sync_product_with_magento = fields.Boolean(
        string="Sync Product with Magento", help="If Checked means, Product " "synced With Magento Product"
    )
    active_product = fields.Boolean(string="Odoo Product Active", related="odoo_product_id.active")
    active = fields.Boolean(string="Active", default=True)
    image_1920 = fields.Image(related="odoo_product_id.image_1920")
    product_template_attribute_value_ids = fields.Many2many(
        related="odoo_product_id.product_template_attribute_value_ids"
    )
    qty_available = fields.Float(related="odoo_product_id.qty_available")
    lst_price = fields.Float(related="odoo_product_id.lst_price")
    standard_price = fields.Float(related="odoo_product_id.standard_price")
    currency_id = fields.Many2one(related="odoo_product_id.currency_id")
    valuation = fields.Selection(related="odoo_product_id.product_tmpl_id.valuation")
    cost_method = fields.Selection(related="odoo_product_id.product_tmpl_id.cost_method")
    company_id = fields.Many2one(related="odoo_product_id.company_id")
    uom_id = fields.Many2one(related="odoo_product_id.uom_id")
    uom_po_id = fields.Many2one(related="odoo_product_id.uom_po_id")
    total_magento_variants = fields.Integer(related="magento_tmpl_id.total_magento_variants")

    _sql_constraints = [
        (
            "_magento_product_unique_constraint",
            "unique(magento_sku,magento_instance_id,magento_product_id,magento_tmpl_id)",
            "Magento Product must be unique",
        )
    ]

    def unlink(self):
        unlink_magento_products = self.env["magento.product.product"]
        unlink_magento_templates = self.env["magento.product.template"]
        for magento_product in self:
            # Check if the product is last product of this template...
            if not unlink_magento_templates or (
                unlink_magento_templates and unlink_magento_templates != magento_product.magento_tmpl_id
            ):
                unlink_magento_templates |= magento_product.magento_tmpl_id
            unlink_magento_products |= magento_product
        res = super(MagentoProductProduct, unlink_magento_products).unlink()
        # delete templates after calling super, as deleting template could lead to deleting
        # products due to ondelete='cascade'
        if not unlink_magento_templates.magento_product_ids:
            unlink_magento_templates.unlink()
        self.clear_caches()
        return res

    def toggle_active(self):
        """Archiving related magento.product.template if there is not any more active magento.product.product
        (and vice versa, unarchiving the related magento product template if there is now an active magento.product.product)"""
        result = super().toggle_active()
        # We deactivate product templates which are active with no active variants.
        tmpl_to_deactivate = self.filtered(
            lambda product: (product.magento_tmpl_id.active and not product.magento_tmpl_id.magento_product_ids)
        ).mapped("magento_tmpl_id")
        # We activate product templates which are inactive with active variants.
        tmpl_to_activate = self.filtered(
            lambda product: (not product.magento_tmpl_id.active and product.magento_tmpl_id.magento_product_ids)
        ).mapped("magento_tmpl_id")
        (tmpl_to_deactivate + tmpl_to_activate).toggle_active()
        return result

    def view_odoo_product(self):
        """
        This method id used to view odoo product.
        :return: Action
        """
        if self.odoo_product_id:
            vals = {
                "name": "Odoo Product",
                "type": "ir.actions.act_window",
                "res_model": "product.product",
                "view_type": "form",
                "view_mode": "tree,form",
                "domain": [("id", "=", self.odoo_product_id.id)],
            }
            return vals

    @staticmethod
    def update_custom_option(item):
        extension = item.get("extension_attributes", {})
        if isinstance(item.get("custom_attributes", []), list):
            attributes = {}
            for attribute in item.get("custom_attributes", []):
                attributes.update({attribute.get("attribute_code"): attribute.get("value")})
            attributes and item.update({"custom_attributes": attributes})
        if isinstance(extension.get("website_wise_product_price_data", []), list):
            prices = []
            for price in extension.get("website_wise_product_price_data", []):
                if isinstance(price, str):
                    prices.append(json.loads(price))
            prices and extension.update({"website_wise_product_price_data": prices})
        return True

    def search_product_in_layer(self, line, item):
        self.update_custom_option(item)
        product_template = self.env["product.template"]
        # product = product.search([("default_code", "=", item.get("sku"))], limit=1)
        product_template = product_template.search(
            [
                "|",
                "|",
                ("default_code", "=", item.get("sku")),
                ("default_code", "=", item.get("sku").upper()),
                ("default_code", "=", item.get("sku").lower()),
            ],
            limit=1,
        )
        m_product = self.search(
            [
                "|",
                ("magento_product_id", "=", item.get("id")),
                ("magento_sku", "=", item.get("sku")),
                ("magento_instance_id", "=", line.instance_id.id),
            ],
            limit=1,
        )
        if not m_product:
            m_product = self.search(
                [
                    "|",
                    ("magento_product_id", "=", item.get("id")),
                    ("magento_sku", "=", item.get("sku")),
                    ("magento_instance_id", "=", line.instance_id.id),
                    ("active", "=", False),
                ],
                limit=1,
            )
            m_product.write({"active": True})
        if product_template:
            m_template = m_product.magento_tmpl_id
            product = m_product.odoo_product_id
            if "is_order" not in list(self.env.context.keys()):
                if not line.do_not_update_existing_product:
                    self.__update_layer_product(line, item, m_product)
                    m_template.update_layer_template(line, item, product)
        else:
            product = self.with_context(is_order=self.env.context.get("is_order", False))._search_odoo_product(
                line, item
            )
        prices = item.get("extension_attributes", {}).get("website_wise_product_price_data", [])
        if "is_order" not in list(self.env.context.keys()):
            if not line.do_not_update_existing_product and prices and product:
                self.__update_prices(prices)
                self.env["magento.product.template"].update_price_list(line, product, prices)
        value = False
        if product and not product.product_breeder_id:
            attribute = item.get("custom_attributes")
            for each in attribute:
                if each == "brand":
                    value = attribute[each]
            product_brand = False
            if value != False:
                product_brand = self.env["product.breeder"].search([("magento_id", "=", value)])
            if not product_brand:
                if value != False:
                    product_brand_attribute = self.env["magento.attribute.option"].search(
                        [("magento_attribute_option_id", "=", value), ("magento_attribute_id", "=", 10)]
                    )
                    product_brand = self.env["product.breeder"].create(
                        {
                            "breeder_name": product_brand_attribute.magento_attribute_option_name,
                            "magento_id": product_brand_attribute.magento_attribute_option_id,
                        }
                    )
            product.product_breeder_id = product_brand.id if product_brand else False
        return product

    @staticmethod
    def __update_prices(prices):
        for price in prices:
            price.update(
                {
                    "price": price.get("product_price"),
                    "currency": price.get("default_store_currency"),
                }
            )

    def __update_layer_product(self, line, item, m_product):
        product = m_product.odoo_product_id
        instance = line.instance_id
        m_template = m_product.magento_tmpl_id
        data = self.magento_tmpl_id.get_website_category_attribute_tax_class(item, instance)
        values = self._prepare_layer_product_values(m_template, product, item, data)
        values.pop("magento_product_id")
        m_product.write(values)
        if instance.allow_import_image_of_products:
            m_template = self.env["magento.product.template"]
            # We will only update/create image in layer and odoo product if customer has
            # enabled the configuration from instance.
            images = m_template.get_product_images(item, data, line)
            m_template.create_layer_image(instance, images, variant=m_product)
        return True

    def _search_odoo_product(self, line, item):
        product = self.env["product.template"]
        # product = product.search([("default_code", "=", item.get("sku"))], limit=1)
        product = product.search(
            [
                "|",
                "|",
                ("default_code", "=", item.get("sku")),
                ("default_code", "=", item.get("sku").upper()),
                ("default_code", "=", item.get("sku").lower()),
            ],
            limit=1,
        )
        product |= product.search(
            [
                "|",
                "|",
                ("default_code", "=", item.get("sku")),
                ("default_code", "=", item.get("sku").upper()),
                ("default_code", "=", item.get("sku").lower()),
                ("active", "=", False),
            ],
            limit=1,
        )
        if not product:
            if not self.env.context.get("is_order", False):
                product = self._create_new_odoo_template(item)
            elif line.instance_id.auto_create_product:
                product = self._create_new_odoo_template(item)
            else:
                # create log and inform that customer has not enabled the
                # auto_create_product in the instance.
                is_verify = self.verify_configuration(line, item)
                return is_verify
        # If product is found then we will create mapping of that odoo product in Magento
        # layer and Magento product
        self._map_product_in_layer(line, item, product)
        return product

    # def _create_odoo_product(self, item):
    #     self.update_custom_option(item)
    #     values = self._prepare_product_values(item)
    #     return self.env["product.product"].create(values)

    def _create_new_odoo_template(self, link):
        # self.update_custom_option(item)
        values = self._prepare_new_product_values(link)
        return self.env["product.template"].create(values)

    def _prepare_new_product_values(self, link):
        values = {
            "name": link.get("name"),
            "default_code": link.get("sku"),
            "type": "product",
            "invoice_policy": "order",
        }
        value = False
        categ = False
        price = 0
        flower_type_value = False
        sex_description_value = False
        phyto_available_value = False
        weight_value = False
        product_category_id = False
        weight_value = link.get("weight")
        attribute = link.get("custom_attributes")
        for each in attribute:
            if each == "brand":
                value = attribute[each]
            if each == "product_type_c":
                categ = attribute[each]
            if each == "seeds_flowering_type":
                flower_type_value = attribute[each]
            if each == "seeds_feminised":
                sex_description_value = attribute[each]
            if each == "phyto_available":
                if each == "1":
                    phyto_available_value = True

        product_brand = False
        if value != False:
            product_brand = self.env["product.breeder"].search([("magento_id", "=", value)])
        if not product_brand:
            if value != False:
                product_brand_attribute = self.env["magento.attribute.option"].search(
                    [("magento_attribute_option_id", "=", value), ("magento_attribute_id", "=", 10)]
                )
                if product_brand_attribute:
                    product_brand = self.env["product.breeder"].create(
                        {
                            "breeder_name": product_brand_attribute.magento_attribute_option_name,
                            "magento_id": product_brand_attribute.magento_attribute_option_id,
                        }
                    )
        if categ != False:
            product_category_id = self.env["product.category"].search([("magento_id", "=", categ)])
        if not product_category_id:
            product_category_id = self.env["product.category"].search([("magento_id", "=", 2241)])
        flower_type_id = self.env["flower.type"].search([("magento_id", "=", flower_type_value)])
        sex_description_id = self.env["product.sex"].search([("magento_id", "=", sex_description_value)])
        for new_price in link["extension_attributes"].get("website_wise_product_price_data"):
            if new_price["product_price"]:
                price = new_price["product_price"]
        values.update(
            {
                "product_breeder_id": product_brand.id if product_brand else False,
                "categ_id": product_category_id.id,
                "retail_default_price": price,
                "flower_type_id": flower_type_id.id,
                "product_sex_id": sex_description_id.id,
                "is_pn_us": phyto_available_value,
                "weight": weight_value,
            }
        )
        # description = self.prepare_description(item)
        # if description:
        #     values.update(description)
        return values

    def _create_odoo_template(self, link):
        # self.update_custom_option(item)
        values = self._prepare_product_values(link)
        return self.env["product.template"].create(values)

    def _prepare_product_values(self, link):
        values = {
            "name": link.get("product_name"),
            "default_code": link.get("simple_product_sku"),
            "type": "product",
            "invoice_policy": "order",
        }
        # description = self.prepare_description(item)
        # if description:
        #     values.update(description)
        return values

    def prepare_description(self, item, is_layer=False):
        description = {}
        ipc = self.env["ir.config_parameter"].sudo()
        ipc = ipc.get_param("odoo_magento2_ept.set_magento_sales_description")
        if ipc:
            attribute = item.get("custom_attributes", {})
            if is_layer:
                description.update(
                    {
                        "description": attribute.get("description"),
                        "short_description": attribute.get("short_description"),
                    }
                )
            else:
                description.update(
                    {
                        "description": attribute.get("description"),
                        "description_sale": attribute.get("short_description"),
                    }
                )
        return description

    def _map_product_in_layer(self, line, item, product):
        template = self.env["magento.product.template"]
        template = template.create_template(line, item, product)
        self._create_product(template, product, item, line)
        return True

    def _create_product(self, template, product, item, line):
        instance = line.instance_id
        data = self.magento_tmpl_id.get_website_category_attribute_tax_class(item, instance)
        values = self._prepare_layer_product_values(template, product, item, data)
        m_product = self.search([("magento_product_id", "=", item.get("id"))], limit=1)
        if not m_product:
            m_product = self.create(values)
        if instance.allow_import_image_of_products:
            m_template = self.env["magento.product.template"]
            # We will only update/create image in layer and odoo product if customer has
            # enabled the configuration from instance.
            images = m_template.get_product_images(item, data, line)
            m_template.create_layer_image(instance, images, variant=m_product)
        return m_product

    def _prepare_layer_product_values(self, template, product, item, data):
        if product._name == "product.template":
            product_id = self.env["product.product"].search([("product_tmpl_id", "=", product[0].id)])
            product_id |= self.env["product.product"].search(
                [("product_tmpl_id", "=", product[0].id), ("active", "=", False)]
            )
        else:
            product_id = product
        values = {
            "odoo_product_id": product_id.id,
            "magento_instance_id": template.magento_instance_id.id,
            "magento_product_id": item.get("id"),
            "magento_sku": item.get("sku"),
            "magento_product_name": item.get("name"),
            "magento_tmpl_id": template.id,
            "created_at": datetime.strptime(item.get("created_at"), "%Y-%m-%d %H:%M:%S").date(),
            "updated_at": datetime.strptime(item.get("created_at"), "%Y-%m-%d %H:%M:%S").date(),
            "product_type": item.get("type_id"),
            "magento_website_ids": [(6, 0, data.get("website"))],
            "sync_product_with_magento": True,
        }
        description = self.prepare_description(item, is_layer=True)
        if description:
            values.update(description)
        return values

    def import_configurable_product(self, line, item, product_values_received={}):
        try:
            template = self.env["product.template"]
            m_template = self.env["magento.product.template"]
            link = item.get("extension_attributes").get("configurable_product_link_data")
            magento_sku = ""
            # if link:
            #     link = json.loads(link[0])
            #     magento_sku = link.get("simple_product_sku")
            if item.get("type_id") == "configurable":
                item.get("sku", False)
                magento_id = item.get("id", False)
                configurable_product_master = self.env["magento.product.configurable"]
                is_exists = configurable_product_master.search([("magento_product_id", "=", magento_id)])
                if not is_exists:
                    attribute_set = self.env["magento.attribute.set"].search(
                        [("attribute_set_id", "=", item.get("attribute_set_id"))]
                    )
                    conf_product = configurable_product_master.create(
                        {
                            "magento_product_id": item.get("id"),
                            "magento_product_name": item.get("name"),
                            "magento_product_type": "Configurable Product",
                            "magento_sku": item.get("sku"),
                            "product_type": attribute_set.attribute_set_name,
                        }
                    )
                    _logger.info(f"Created configurable product {conf_product} {conf_product.magento_product_name}")
            self.__update_child_response(item)
            for child_product_data in link:
                child_product_data = json.loads(child_product_data)
                magento_sku = child_product_data.get("simple_product_sku")
                m_template = m_template.search(
                    [
                        ("magento_product_template_id", "=", child_product_data.get("simple_product_id")),
                        ("magento_instance_id", "=", line.instance_id.id),
                    ],
                    limit=1,
                )
                m_template |= m_template.search(
                    [
                        ("magento_product_template_id", "=", child_product_data.get("simple_product_id")),
                        ("magento_instance_id", "=", line.instance_id.id),
                        ("active", "=", False),
                    ],
                    limit=1,
                )
                template = False
                if not template:
                    template = self.search_odoo_product_template_exists(
                        magento_sku, child_product_data, product_values_received
                    )
                    if not template:
                        # is_verify = self.verify_configuration(line, item)
                        # if is_verify:

                        template = self._create_odoo_template(child_product_data)
                        value = False
                        categ = False
                        price = 0
                        flower_type_value = False
                        seeds_pack_value = False
                        sex_description_value = False
                        phyto_available_value = False
                        weight_value = False
                        pack_size = False
                        product_category_id = False
                        seeds_variety_value = False
                        seeds_thc_filter_value = False
                        seeds_cbd_filter_value = False
                        seeds_yield_filter_value = False
                        seeds_yield_indoor_filter_value = False
                        seeds_plant_height_value = False
                        seeds_flowering_weeks_value = False
                        seeds_climate_value = False
                        seeds_odour_value = False
                        seeds_grows_value = False
                        seeds_cannabinoid_report_value = False
                        seeds_auto_harvest_time_value = False
                        seeds_grow_difficulty_value = False
                        seeds_bud_formation_value = False
                        seeds_award_filter_value = False
                        seeds_mould_value = False
                        seeds_extracts_value = False
                        seeds_taste_filter_value = False
                        seeds_terpenes_value = False
                        genetic_discription_value = False

                        seeds_variety = False
                        seeds_thc_filter = False
                        seeds_cbd_filter = False
                        seeds_yield_filter = False
                        seeds_yield_indoor_filter = False
                        seeds_plant_height = False
                        seeds_flowering_weeks = False
                        seeds_auto_harvest_time = False
                        seeds_climate = False
                        seeds_odour = False
                        seeds_grow_difficulty = False
                        seeds_cannabinoid_report = False
                        seeds_grows = False
                        seeds_bud_formation = False
                        seeds_award_filter = False
                        seeds_mould = False
                        seeds_extracts = False
                        seeds_taste_filter = False
                        seeds_terpenes = False

                        # if child_product_data.get('simple_product_attribute'):
                        #     for record in child_product_data.get('simple_product_attribute'):
                        #         seeds_pack_value = record['value']
                        weight_value = item.get("weight")
                        attribute = item.get("custom_attributes")
                        for each in attribute:
                            if each["attribute_code"] == "brand":
                                value = each["value"]
                            if each["attribute_code"] == "product_type_c":
                                categ = each["value"]
                            if each["attribute_code"] == "seeds_flowering_type":
                                flower_type_value = each["value"]
                            if each["attribute_code"] == "seeds_number":
                                seeds_pack_value = each["value"]
                            if each["attribute_code"] == "seeds_feminised":
                                sex_description_value = each["value"]
                            if each["attribute_code"] == "phyto_available":
                                if each["value"] == "1":
                                    phyto_available_value = True
                            if each["attribute_code"] == "seeds_variety":
                                seeds_variety_value = each["value"]
                            if each["attribute_code"] == "seeds_thc_filter":
                                seeds_thc_filter_value = each["value"]
                            if each["attribute_code"] == "seeds_cbd_filter":
                                seeds_cbd_filter_value = each["value"]
                            if each["attribute_code"] == "seeds_yield_filter":
                                seeds_yield_filter_value = each["value"]
                            if each["attribute_code"] == "seeds_yield_indoor_filter":
                                seeds_yield_indoor_filter_value = each["value"]
                            if each["attribute_code"] == "seeds_plant_height":
                                seeds_plant_height_value = each["value"]
                            if each["attribute_code"] == "seeds_flowering_time":
                                seeds_flowering_weeks_value = each["value"]
                            if each["attribute_code"] == "seeds_climate":
                                seeds_climate_value = each["value"]
                            if each["attribute_code"] == "seeds_odour":
                                seeds_odour_value = each["value"]
                            if each["attribute_code"] == "seeds_grows":
                                seeds_grows_value = each["value"]
                            if each["attribute_code"] == "seeds_cannabinoid_report":
                                seeds_cannabinoid_report_value = each["value"]
                            if each["attribute_code"] == "seeds_auto_harvest_time":
                                seeds_auto_harvest_time_value = each["value"]
                            if each["attribute_code"] == "seeds_grow_difficulty":
                                seeds_grow_difficulty_value = each["value"]
                            if each["attribute_code"] == "seeds_bud_formation":
                                seeds_bud_formation_value = each["value"]
                            if each["attribute_code"] == "seeds_award_filter":
                                seeds_award_filter_value = each["value"]
                            if each["attribute_code"] == "seeds_mould":
                                seeds_mould_value = each["value"]
                            if each["attribute_code"] == "seeds_extracts":
                                seeds_extracts_value = each["value"]
                            if each["attribute_code"] == "seeds_taste_filter":
                                seeds_taste_filter_value = each["value"]
                            if each["attribute_code"] == "seeds_terpenes":
                                seeds_terpenes_value = each["value"]
                            if each["attribute_code"] == "genetic_discription":
                                genetic_discription_value = each["value"]
                        product_brand = False
                        if value != False:
                            product_brand = self.env["product.breeder"].search([("magento_id", "=", value)])
                        if not product_brand:
                            if value != False:
                                product_brand_attribute = self.env["magento.attribute.option"].search(
                                    [("magento_attribute_option_id", "=", value), ("magento_attribute_id", "=", 10)]
                                )
                                if product_brand_attribute:
                                    product_brand = self.env["product.breeder"].create(
                                        {
                                            "breeder_name": product_brand_attribute.magento_attribute_option_name,
                                            "magento_id": product_brand_attribute.magento_attribute_option_id,
                                        }
                                    )
                        if categ != False:
                            product_category_id = self.env["product.category"].search([("magento_id", "=", categ)])
                        if not product_category_id:
                            product_category_id = self.env["product.category"].search([("magento_id", "=", 2241)])
                        flower_type_id = self.env["flower.type"].search([("magento_id", "=", flower_type_value)])
                        sex_description_id = self.env["product.sex"].search(
                            [("magento_id", "=", sex_description_value)]
                        )
                        attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_number")]
                        )
                        pack_size = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_pack_value),
                                ("magento_attribute_id", "=", attribute_id.id),
                            ]
                        )

                        # seeds_variety attribute
                        seeds_variety_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_variety")],limit=1)
                        seeds_variety_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_variety_value),
                                ("magento_attribute_id", "=", seeds_variety_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_variety_attribute_option:
                            seeds_variety = self.env["seeds.variety"].search([("magento_attribute_option_id",'=',seeds_variety_attribute_option.magento_attribute_option_id)])
                            if not seeds_variety:
                                seeds_variety = self.env["seeds.variety"].create(
                                        {
                                            "name": seeds_variety_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_variety_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_variety_attribute_option.magento_attribute_option_id
                                        }
                                    )
                                
                        # seeds_thc_filter attribute
                        seeds_thc_filter_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_thc_filter")],limit=1
                        )
                        seeds_thc_filter_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_thc_filter_value),
                                ("magento_attribute_id", "=", seeds_thc_filter_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_thc_filter_attribute_option:
                            seeds_thc_filter = self.env["seeds.thc.filter"].search([("magento_attribute_option_id",'=',seeds_thc_filter_attribute_option.magento_attribute_option_id)])
                            if not seeds_thc_filter:
                                seeds_thc_filter = self.env["seeds.thc.filter"].create(
                                        {
                                            "name": seeds_thc_filter_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_thc_filter_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_thc_filter_attribute_option.magento_attribute_option_id
                                        }
                                    )
                                
                        # seeds_cbd_filter attribute
                        seeds_cbd_filter_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_cbd_filter")],limit=1
                        )
                        seeds_cbd_filter_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_cbd_filter_value),
                                ("magento_attribute_id", "=", seeds_cbd_filter_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_cbd_filter_attribute_option:
                            seeds_cbd_filter = self.env["seeds.cbd.filter"].search([("magento_attribute_option_id",'=',seeds_cbd_filter_attribute_option.magento_attribute_option_id)])
                            if not seeds_cbd_filter:
                                seeds_cbd_filter = self.env["seeds.cbd.filter"].create(
                                        {
                                            "name": seeds_cbd_filter_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_cbd_filter_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_cbd_filter_attribute_option.magento_attribute_option_id
                                        }
                                    )
                        
                        # seeds_yield_filter attribute
                        seeds_yield_filter_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_yield_filter")],limit=1
                        )
                        seeds_yield_filter_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_yield_filter_value),
                                ("magento_attribute_id", "=", seeds_yield_filter_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_yield_filter_attribute_option:
                            seeds_yield_filter = self.env["seeds.yield.filter"].search([("magento_attribute_option_id",'=',seeds_yield_filter_attribute_option.magento_attribute_option_id)])
                            if not seeds_yield_filter:
                                seeds_yield_filter = self.env["seeds.yield.filter"].create(
                                        {
                                            "name": seeds_yield_filter_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_yield_filter_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_yield_filter_attribute_option.magento_attribute_option_id
                                        }
                                    )
                        
                        # seeds_yield_indoor_filter attribute
                        seeds_yield_indoor_filter_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_yield_indoor_filter")],limit=1
                        )
                        seeds_yield_indoor_filter_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_yield_indoor_filter_value),
                                ("magento_attribute_id", "=", seeds_yield_indoor_filter_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_yield_indoor_filter_attribute_option:
                            seeds_yield_indoor_filter = self.env["seeds.yield.indoor.filter"].search([("magento_attribute_option_id",'=',seeds_yield_indoor_filter_attribute_option.magento_attribute_option_id)])
                            if not seeds_yield_indoor_filter:
                                seeds_yield_indoor_filter = self.env["seeds.yield.indoor.filter"].create(
                                        {
                                            "name": seeds_yield_indoor_filter_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_yield_indoor_filter_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_yield_indoor_filter_attribute_option.magento_attribute_option_id
                                        }
                                    )
                        # seeds_plant_height attribute
                        seeds_plant_height_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_plant_height")],limit=1
                        )
                        seeds_plant_height_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_plant_height_value),
                                ("magento_attribute_id", "=", seeds_plant_height_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_plant_height_attribute_option:
                            seeds_plant_height = self.env["seeds.plant.height"].search([("magento_attribute_option_id",'=',seeds_plant_height_attribute_option.magento_attribute_option_id)])
                            if not seeds_plant_height:
                                seeds_plant_height = self.env["seeds.plant.height"].create(
                                        {
                                            "name": seeds_plant_height_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_plant_height_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_plant_height_attribute_option.magento_attribute_option_id
                                        }
                                    )
                                
                        # seeds_flowering_weeks attribute
                        seeds_flowering_weeks_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_flowering_weeks")],limit=1
                        )
                        seeds_flowering_weeks_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_flowering_weeks_value),
                                ("magento_attribute_id", "=", seeds_flowering_weeks_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_flowering_weeks_attribute_option:
                            seeds_flowering_weeks = self.env["seeds.flowering.weeks"].search([("magento_attribute_option_id",'=',seeds_flowering_weeks_attribute_option.magento_attribute_option_id)])
                            if not seeds_flowering_weeks:
                                seeds_flowering_weeks = self.env["seeds.flowering.weeks"].create(
                                        {
                                            "name": seeds_flowering_weeks_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_flowering_weeks_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_flowering_weeks_attribute_option.magento_attribute_option_id
                                        }
                                    )
                        # seeds_auto_harvest_time attribute
                        seeds_auto_harvest_time_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_auto_harvest_time")],limit=1
                        )
                        seeds_auto_harvest_time_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_auto_harvest_time_value),
                                ("magento_attribute_id", "=", seeds_auto_harvest_time_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_auto_harvest_time_attribute_option:
                            seeds_auto_harvest_time = self.env["seeds.auto.harvest.time"].search([("magento_attribute_option_id",'=',seeds_auto_harvest_time_attribute_option.magento_attribute_option_id)])
                            if not seeds_auto_harvest_time:
                                seeds_auto_harvest_time = self.env["seeds.auto.harvest.time"].create(
                                        {
                                            "name": seeds_auto_harvest_time_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_auto_harvest_time_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_auto_harvest_time_attribute_option.magento_attribute_option_id
                                        }
                                    )

                        
                        # seeds_climate attribute
                        seeds_climate_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_climate")],limit=1)
                        seeds_climate_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_climate_value),
                                ("magento_attribute_id", "=", seeds_climate_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_climate_attribute_option:
                            seeds_climate = self.env["seeds.climate"].search([("magento_attribute_option_id",'=',seeds_climate_attribute_option.magento_attribute_option_id)])
                            if not seeds_climate:
                                seeds_climate = self.env["seeds.climate"].create(
                                        {
                                            "name": seeds_climate_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_climate_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_climate_attribute_option.magento_attribute_option_id
                                        }
                                    )
                        # seeds_odour attribute
                        seeds_odour_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_odour")],limit=1)
                        seeds_odour_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_odour_value),
                                ("magento_attribute_id", "=", seeds_odour_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_odour_attribute_option:
                            seeds_odour = self.env["seeds.odour"].search([("magento_attribute_option_id",'=',seeds_odour_attribute_option.magento_attribute_option_id)])
                            if not seeds_odour:
                                seeds_odour = self.env["seeds.odour"].create(
                                        {
                                            "name": seeds_odour_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_odour_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_odour_attribute_option.magento_attribute_option_id
                                        }
                                    )

                        # seeds_grow_difficulty attribute
                        seeds_grow_difficulty_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_grow_difficulty")],limit=1
                        )
                        seeds_grow_difficulty_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_grow_difficulty_value),
                                ("magento_attribute_id", "=", seeds_grow_difficulty_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_grow_difficulty_attribute_option:
                            seeds_grow_difficulty = self.env["seeds.grow.difficulty"].search([("magento_attribute_option_id",'=',seeds_grow_difficulty_attribute_option.magento_attribute_option_id)])
                            if not seeds_grow_difficulty:
                                seeds_grow_difficulty = self.env["seeds.grow.difficulty"].create(
                                        {
                                            "name": seeds_grow_difficulty_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_grow_difficulty_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_grow_difficulty_attribute_option.magento_attribute_option_id
                                        }
                                    )
                        
                        # seeds_cannabinoid_report attribute
                        seeds_cannabinoid_report_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_cannabinoid_report")],limit=1
                        )
                        seeds_cannabinoid_report_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_cannabinoid_report_value),
                                ("magento_attribute_id", "=", seeds_cannabinoid_report_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_cannabinoid_report_attribute_option:
                            seeds_cannabinoid_report = self.env["seeds.cannabinoid.report"].search([("magento_attribute_option_id",'=',seeds_cannabinoid_report_attribute_option.magento_attribute_option_id)])
                            if not seeds_cannabinoid_report:
                                seeds_cannabinoid_report = self.env["seeds.cannabinoid.report"].create(
                                        {
                                            "name": seeds_cannabinoid_report_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_cannabinoid_report_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_cannabinoid_report_attribute_option.magento_attribute_option_id
                                        }
                                    )
                        # seeds_grows attribute
                        seeds_grows_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_grows")],limit=1)
                        seeds_grows_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_grows_value),
                                ("magento_attribute_id", "=", seeds_grows_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_grows_attribute_option:
                            seeds_grows = self.env["seeds.grows"].search([("magento_attribute_option_id",'=',seeds_grows_attribute_option.magento_attribute_option_id)])
                            if not seeds_grows:
                                seeds_grows = self.env["seeds.grows"].create(
                                        {
                                            "name": seeds_grows_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_grows_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_grows_attribute_option.magento_attribute_option_id
                                        }
                                    )
                        # seeds_bud_formation attribute
                        seeds_bud_formation_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_bud_formation")],limit=1
                        )
                        seeds_bud_formation_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_bud_formation_value),
                                ("magento_attribute_id", "=", seeds_bud_formation_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_bud_formation_attribute_option:
                            seeds_bud_formation = self.env["seeds.bud.formation"].search([("magento_attribute_option_id",'=',seeds_bud_formation_attribute_option.magento_attribute_option_id)])
                            if not seeds_bud_formation:
                                seeds_bud_formation = self.env["seeds.bud.formation"].create(
                                        {
                                            "name": seeds_bud_formation_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_bud_formation_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_bud_formation_attribute_option.magento_attribute_option_id
                                        }
                                    )
                        # seeds_award_filter attribute
                        seeds_award_filter_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_award_filter")],limit=1
                        )
                        seeds_award_filter_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_award_filter_value),
                                ("magento_attribute_id", "=", seeds_award_filter_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_award_filter_attribute_option:
                            seeds_award_filter = self.env["seeds.award.filter"].search([("magento_attribute_option_id",'=',seeds_award_filter_attribute_option.magento_attribute_option_id)])
                            if not seeds_award_filter:
                                seeds_award_filter = self.env["seeds.award.filter"].create(
                                        {
                                            "name": seeds_award_filter_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_award_filter_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_award_filter_attribute_option.magento_attribute_option_id
                                        }
                                    )
                                
                        # seeds_mould attribute
                        seeds_mould_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_mould")],limit=1)
                        seeds_mould_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_mould_value),
                                ("magento_attribute_id", "=", seeds_mould_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_mould_attribute_option:
                            seeds_mould = self.env["seeds.mould"].search([("magento_attribute_option_id",'=',seeds_mould_attribute_option.magento_attribute_option_id)])
                            if not seeds_mould:
                                seeds_mould = self.env["seeds.mould"].create(
                                        {
                                            "name": seeds_mould_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_mould_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_mould_attribute_option.magento_attribute_option_id
                                        }
                                    )
                        # seeds_extracts attribute
                        seeds_extracts_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_extracts")],limit=1
                        )
                        seeds_extracts_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_extracts_value),
                                ("magento_attribute_id", "=", seeds_extracts_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_extracts_attribute_option:
                            seeds_extracts = self.env["seeds.extracts"].search([("magento_attribute_option_id",'=',seeds_extracts_attribute_option.magento_attribute_option_id)])
                            if not seeds_extracts:
                                seeds_extracts = self.env["seeds.extracts"].create(
                                        {
                                            "name": seeds_extracts_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_extracts_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_extracts_attribute_option.magento_attribute_option_id
                                        }
                                    )
                        # seeds_taste_filter attribute
                        seeds_taste_filter_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_taste_filter")],limit=1
                        )
                        seeds_taste_filter_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_taste_filter_value),
                                ("magento_attribute_id", "=", seeds_taste_filter_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_taste_filter_attribute_option:
                            seeds_taste_filter = self.env["seeds.taste.filter"].search([("magento_attribute_option_id",'=',seeds_taste_filter_attribute_option.magento_attribute_option_id)])
                            if not seeds_taste_filter:
                                seeds_taste_filter = self.env["seeds.taste.filter"].create(
                                        {
                                            "name": seeds_taste_filter_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_taste_filter_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_taste_filter_attribute_option.magento_attribute_option_id
                                        }
                                    )
                        # seeds_terpenes attribute
                        seeds_terpenes_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "seeds_terpenes")],limit=1
                        )
                        seeds_terpenes_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", seeds_terpenes_value),
                                ("magento_attribute_id", "=", seeds_terpenes_attribute_id.id),
                            ],limit=1
                        )
                        if seeds_terpenes_attribute_option:
                            seeds_terpenes = self.env["seeds.terpenes"].search([("magento_attribute_option_id",'=',seeds_terpenes_attribute_option.magento_attribute_option_id)])
                            if not seeds_terpenes:
                                seeds_terpenes = self.env["seeds.terpenes"].create(
                                        {
                                            "name": seeds_terpenes_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": seeds_terpenes_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":seeds_terpenes_attribute_option.magento_attribute_option_id
                                        }
                                    )
                        
                        # genetic_discription attribute
                        genetic_discription = False
                        genetic_discription_attribute_id = self.env["magento.product.attribute"].search(
                            [("magento_attribute_code", "=", "genetic_discription")],limit=1
                        )
                        genetic_discription_attribute_option = self.env["magento.attribute.option"].search(
                            [
                                ("magento_attribute_option_id", "=", genetic_discription_value),
                                ("magento_attribute_id", "=", genetic_discription_attribute_id.id),
                            ],limit=1
                        )
                        if genetic_discription_attribute_option:
                            genetic_discription = self.env["genetic.discription"].search([("magento_attribute_option_id",'=',genetic_discription_attribute_option.magento_attribute_option_id)])
                            if not genetic_discription:
                                genetic_discription = self.env["genetic.discription"].create(
                                        {
                                            "name": genetic_discription_attribute_option.magento_attribute_option_name,
                                            "magento_attribute_id": genetic_discription_attribute_option.magento_attribute_id.id,
                                            "magento_attribute_option_id":genetic_discription_attribute_option.magento_attribute_option_id
                                        }
                                    )

                        for new_price in child_product_data.get("website_wise_product_price_data"):
                            if new_price["price"]:
                                price = new_price["price"]
                        template.write(
                            {
                                "product_breeder_id": product_brand.id if product_brand else False,
                                "categ_id": product_category_id.id,
                                "retail_default_price": price,
                                "flower_type_id": flower_type_id.id,
                                "product_sex_id": sex_description_id.id,
                                "is_pn_us": phyto_available_value,
                                "pack_size_desc": pack_size.magento_attribute_option_name,
                                "weight": weight_value,
                                "seeds_variety_id":seeds_variety.id if seeds_variety else False,
                                "seeds_thc_filter_id":seeds_thc_filter.id if seeds_thc_filter else False,
                                "seeds_cbd_filter_id":seeds_cbd_filter.id if seeds_cbd_filter else False,
                                "seeds_yield_filter_id":seeds_yield_filter.id if seeds_yield_filter else False,
                                "seeds_yield_indoor_filter_id":seeds_yield_indoor_filter.id if seeds_yield_indoor_filter else False,
                                "seeds_plant_height_id":seeds_plant_height.id if seeds_plant_height else False,
                                "seeds_flowering_weeks_id":seeds_flowering_weeks.id if seeds_flowering_weeks else False,
                                "seeds_auto_harvest_time_id":seeds_auto_harvest_time.id if seeds_auto_harvest_time else False,
                                "seeds_climate_id":seeds_climate.id if seeds_climate else False,
                                "seeds_odour_id":seeds_odour.id if seeds_odour else False,
                                "seeds_grow_difficulty_id":seeds_grow_difficulty.id if seeds_grow_difficulty else False,
                                "seeds_cannabinoid_report_id":seeds_cannabinoid_report.id if seeds_cannabinoid_report else False,
                                "seeds_grows_id":seeds_grows.id if seeds_grows else False,
                                "seeds_bud_formation_id":seeds_bud_formation.id if seeds_bud_formation else False,
                                "seeds_award_filter_id":seeds_award_filter.id if seeds_award_filter else False,
                                "seeds_mould_id":seeds_mould.id if seeds_mould else False,
                                "seeds_extracts_id":seeds_extracts.id if seeds_extracts else False,
                                "seeds_taste_filter_id":seeds_taste_filter.id if seeds_taste_filter else False,
                                "seeds_terpenes_id":seeds_terpenes.id if seeds_terpenes else False,
                                "genetic_discription_id": genetic_discription.id if genetic_discription else False,
                                
                            }
                        )

                    else:
                        if template._name == "product.product":
                            temp_id = template.product_tmpl_id.id
                        else:
                            temp_id = template.id
                        # value = False
                        # attribute = item.get("custom_attributes")
                        # for each in attribute:
                        #     if each['attribute_code'] == 'brand':
                        #         value = each['value']
                        # product_brand = self.env['product.breeder'].search([("magento_id",'=',value)])

                        m_template.write({"odoo_product_template_id": temp_id})

                if not m_template:
                    m_template = m_template.search(
                        [
                            ("magento_sku", "=", child_product_data.get("simple_product_sku")),
                        ],
                        limit=1,
                    )
                    if not m_template:
                        values = {
                            "magento_product_name": child_product_data.get("product_name"),
                            "magento_instance_id": line.instance_id.id,
                            "magento_sku": child_product_data.get("simple_product_sku"),
                            "magento_product_template_id": child_product_data.get("simple_product_id"),
                            "product_type": child_product_data.get("product_type"),
                            "sync_product_with_magento": True,
                            "odoo_product_template_id": template.id,
                        }
                        m_template = m_template.create(values)
                    else:
                        m_template.write({"active": True, "sync_product_with_magento": True})
        except Exception:
            pass
        return True
        # if not m_template:
        #     m_template = self.search(
        #         [("magento_sku", "=", magento_sku), ("magento_instance_id", "=", line.instance_id.id)]
        #     ).magento_tmpl_id
        # if template:
        #     return m_template.create_configurable_template(line, item, template)
        # elif not template:
        #     return self.search_odoo_product_template_exists(magento_sku, item)
        # else:
        #     # Create log for do not update product
        #     return self.verify_configuration(line, item)

    def search_odoo_product_template_exists(self, magento_sku, item, product_values_received={}):
        """
        Search Odoo product template exists or not.
        :param magento_sku: SKU received from Magento
        :param item: item received from Magento
        :return: odoo product template object or False
        """
        product_obj = self.env["product.template"]
        magento_product_obj = self.env["magento.product.product"]
        magento_product_product = magento_product_obj.search(
            [
                "|",
                "|",
                ("magento_sku", "=", magento_sku),
                ("magento_sku", "=", magento_sku.upper()),
                ("magento_sku", "=", magento_sku.lower()),
            ]
        )
        if magento_product_product:
            existing_products = magento_product_product.odoo_product_id
        else:
            existing_products = product_obj.search(
                [
                    "|",
                    "|",
                    ("default_code", "=", magento_sku),
                    ("default_code", "=", magento_sku.upper()),
                    ("default_code", "=", magento_sku.lower()),
                ]
            )
            existing_products |= product_obj.search(
                [
                    "|",
                    "|",
                    ("default_code", "=", magento_sku),
                    ("default_code", "=", magento_sku.upper()),
                    ("default_code", "=", magento_sku.lower()),
                    ("active", "=", False),
                ]
            )
        if not existing_products:
            # not getting product.product record using SKU then search in magento.product.product.
            # product not exist in odoo variant but exist in magento variant layer
            magento_product_template = self.search(
                [
                    "|",
                    "|",
                    ("magento_sku", "=", item.get("simple_product_sku")),
                    ("magento_sku", "=", item.get("simple_product_sku").upper()),
                    ("magento_sku", "=", item.get("simple_product_sku").lower()),
                ],
                limit=1,
            )
            odoo_template_id = (
                magento_product_template.magento_tmpl_id.odoo_product_template_id if magento_product_template else False
            )
        else:
            odoo_template_id = existing_products and existing_products[0]

        if odoo_template_id:
            value_n = False
            seeds_pack_value = False
            flower_type_value = False
            sex_desc_value = False
            attribute = product_values_received.get("custom_attributes")
            for each in attribute:
                if each["attribute_code"] == "brand":
                    value_n = each["value"]
                if each["attribute_code"] == "seeds_number":
                    seeds_pack_value = each["value"]
                if each["attribute_code"] == "seeds_flowering_type":
                    flower_type_value = each["value"]
                if each["attribute_code"] == "seeds_feminised":
                    sex_desc_value = each["value"]
            product_brand = False
            if value_n != False:
                product_brand = self.env["product.breeder"].search([("magento_id", "=", value_n)])
            if not product_brand:
                if value_n != False:
                    product_brand_attribute = self.env["magento.attribute.option"].search(
                        [("magento_attribute_option_id", "=", value_n), ("magento_attribute_id", "=", 10)]
                    )
                    product_brand = self.env["product.breeder"].create(
                        {
                            "breeder_name": product_brand_attribute.magento_attribute_option_name,
                            "magento_id": product_brand_attribute.magento_attribute_option_id,
                        }
                    )
            attribute_id = self.env["magento.product.attribute"].search(
                [("magento_attribute_code", "=", "seeds_number")]
            )
            pack_size = self.env["magento.attribute.option"].search(
                [("magento_attribute_option_id", "=", seeds_pack_value), ("magento_attribute_id", "=", attribute_id.id)]
            )
            flower_type = self.env["flower.type"].search([("magento_id", "=", flower_type_value)])
            sex_desc = self.env["product.sex"].search([("magento_id", "=", sex_desc_value)])
            if not (odoo_template_id.product_breeder_id and odoo_template_id.flower_type_id):
                odoo_template_id.write(
                    {
                        "product_breeder_id": product_brand.id if product_brand else False,
                        "flower_type_id": flower_type.id if flower_type else False,
                    }
                )
            if pack_size:
                odoo_template_id.write(
                    {
                        "pack_size_desc": pack_size.magento_attribute_option_name if pack_size != odoo_template_id.pack_size_desc else odoo_template_id.pack_size_desc,
                    }
                )
            if sex_desc:
                odoo_template_id.write(
                    {
                        "product_sex_id": sex_desc.id if sex_desc else False,
                    }
                )
        return odoo_template_id

    def verify_configuration(self, line, item):
        log = line.queue_id.log_book_id
        instance = line.instance_id
        if not instance.auto_create_product:
            message = (
                f"Odoo Product Not found for SKU : {item.get('sku')}, \n"
                f"And 'Auto Create Product' configuration is off. \n"
                f"Go to Settings -> Select Instance -> Enable the 'Auto Create Product'."
                f"configuration."
            )
            key = "import_product_queue_line_id"
            if "is_order" in (self.env.context.keys()):
                key = "magento_order_data_queue_line_id"
            log.write(
                {
                    "log_lines": [
                        (
                            0,
                            0,
                            {
                                "message": message,
                                "order_ref": item.get("increment_id", ""),
                                "default_code": item.get("sku"),
                                key: line.id,
                            },
                        )
                    ]
                }
            )
            line.queue_id.write({"is_process_queue": False})
            self._cr.commit()
            return False
        return True

    @staticmethod
    def __update_child_response(item):
        attributes = item.get("extension_attributes")
        keys = {"child_products": "configurable_product_link_data", "attributes": "configurable_product_options_data"}
        for key, value in keys.items():
            data = []
            if value in list(attributes.keys()):
                for child in attributes.get(keys.get(key), []):
                    data.append(json.loads(child))
            item.get("extension_attributes", {}).update({key: data})
            item.get("extension_attributes", {}).pop(value)
        return True

    def get_products(self, instance, ids, line):
        args = ""
        for id in ids:
            args += f"{id},"
        url = (
            f"/V1/products?searchCriteria[filterGroups][0][filters][0][field]=entity_id"
            f"&searchCriteria[filterGroups][0][filters][0][condition_type]=in"
            f"&searchCriteria[filterGroups][0][filters][0][value]={args}"
        )
        response = {}
        try:
            _logger.info("Sending request to get Configurable product of Child....")
            response = req(instance, url, is_raise=True)
        except Exception as error:
            _logger.error(error)
        if response:
            response = response.get("items", [])
            return self.__verify_product_response(response, ids, line)
        return response

    def __verify_product_response(self, response, ids, line):
        log = line.queue_id.log_book_id
        response_ids = [item.get("id") for item in response]
        key = "default_code"
        field = "import_product_queue_line_id"
        if "is_order" in list(self.env.context.keys()):
            key = "order_ref"
            field = "magento_order_data_queue_line_id"
        for id in ids:
            if isinstance(id, str):
                id = int(id)
            if id not in response_ids:
                message = f"Magento Product Not found for ID {id}"
                log.write(
                    {
                        "log_lines": [
                            (
                                0,
                                0,
                                {
                                    "message": message,
                                    key: line.magento_id if key == "order_ref" else line.product_sku,
                                    field: line.id,
                                },
                            )
                        ]
                    }
                )
                return []
        return response

    def search_service_product(self, item, line):
        log = line.queue_id.log_book_id
        is_order = bool("is_order" in list(self.env.context.keys()))
        o_product = self.env["product.product"]
        m_product = self.env["magento.product.product"]
        m_product = m_product.search([("magento_product_id", "=", item.get("id"))], limit=1)
        if m_product:
            o_product = m_product.odoo_product_id
        if not o_product:
            o_product = o_product.search([("default_code", "=", item.get("sku"))], limit=1)
        if o_product:
            self.update_custom_option(item)
            self._map_product_in_layer(line, item, o_product)
        elif is_order:
            message = _(
                f"""
                        -Order {item.get('increment_id')} was skipped because when importing
                        order the product {item.get('sku')} could not find in the odoo.
                        -Please create the product in Odoo with the same SKU to import the order.
                        """
            )
            log.write(
                {
                    "log_lines": [
                        (
                            0,
                            0,
                            {
                                "message": message,
                                "order_ref": item.get("increment_id", ""),
                                "magento_order_data_queue_line_id": line.id,
                            },
                        )
                    ]
                }
            )
            return False
        elif not is_order:
            message = _(
                f"Product SKU: {item.get('sku')} and Product Type: {item.get('type_id')}"
                f"is not found in the odoo.\n"
                f"Please create the product in Odoo with the same SKU to map the product "
                f"in layer."
            )
            log.write(
                {
                    "log_lines": [
                        (
                            0,
                            0,
                            {
                                "message": message,
                                "default_code": item.get("sku", ""),
                                "import_product_queue_line_id": line.id,
                            },
                        )
                    ]
                }
            )
            return False
        return True

    def update_magento_product(self, item, magento_websites, instance, magento_product):
        """
        magento product found, then prepare the new magento product vals and write it
        :param item: product item API response
        :param magento_websites: website data
        :param instance:  magento instance
        :param magento_product: magento product object
        :return:
        """
        values = self.prepare_magento_product_vals(item, magento_websites, instance.id)
        values.update(
            {
                "magento_product_id": item.get("id"),
                "magento_tmpl_id": magento_product.magento_tmpl_id.id,
                "odoo_product_id": magento_product.odoo_product_id.id,
                "sync_product_with_magento": True,
            }
        )
        # Below code is for all the configurable's simple product is only simple product in odoo
        # not map all this odoo simple with configurable's simple product
        # and import configurable product, so set all the simple product's id and sync as true
        # in magento.product.template
        magento_product_tmpl = self.env["magento.product.template"].search(
            [
                ("magento_product_template_id", "=", False),
                ("sync_product_with_magento", "=", False),
                ("magento_sku", "=", magento_product.magento_sku),
            ]
        )
        if magento_product_tmpl:
            magento_product_tmpl.write(
                {"magento_product_template_id": item.get("id"), "sync_product_with_magento": True}
            )
        magento_product.write(values)

    def map_odoo_product_with_magento_product(
        self, instance, magento_product, item, log_book_id, order_ref, queue_line, order_data_queue_line_id, error
    ):
        """
        Map Odoo Product with existing Magneto Product in Layer
        :param instance: Magento Instance Object
        :param magento_product: Magento product product object
        :param item: Response received from Magento
        :param log_book_id: Common log book object
        :param order_ref: Order reference
        :param queue_line: product or order queue line
        :param order_data_queue_line_id: data queue line object
        :param error: True if error else False
        :return: Log book id, error
        """
        magento_sku = item.get("sku")
        odo_product = magento_product.odoo_product_id.filtered(lambda x: x.default_code == magento_sku)
        if not odo_product:
            odoo_product, error = self.create_odoo_product(
                magento_sku, item, instance, log_book_id, order_ref, queue_line, order_data_queue_line_id, error
            )
            if odoo_product:
                magento_product.write({"odoo_product_id": [(0, 0, [odoo_product])]})
        return error

    def import_product_inventory(self, instance, auto_apply):
        """
        This method is used to import product stock from magento,
        when Multi inventory sources is not available.
        It will create a product inventory.
        :param instance: Instance of Magento
        :param validate_stock: Stock Validation confirmation
        :return: True
        """
        quant = self.env["stock.quant"]
        log = self.env["common.log.book.ept"]
        warehouse = instance.import_stock_warehouse
        location = warehouse and warehouse.lot_stock_id
        if location:
            api_url = "/V1/stockItems/lowStock?scopeId=0&qty=10000000000&pageSize=100000"
            response = req(instance, api_url)
            stock_data = self.prepare_import_stock_dict(response, instance)
            product_qty = stock_data.get("product_qty")
            consumable = stock_data.get("consumable")
            if product_qty:
                name = f'Inventory For Instance "{instance.name}" And Magento Location ' f'"{warehouse.name}"'
                quant.create_inventory_adjustment_ept(product_qty, location, auto_apply, name)
            if consumable:
                model_id = self.env["common.log.lines.ept"].get_model_id("stock.quant")
                log = log.create_common_log_book("import", "magento_instance_id", instance, model_id, "magento_ept")
                self.create_consumable_products_log(consumable, log)
        else:
            raise UserError(_(f"Please Choose Import product stock for {warehouse.name} location"))
        return log

    def import_product_multi_inventory(self, instance, m_locations, auto_apply):
        """
        This method is used to import product stock from magento,
        when Multi inventory sources is available.
        It will create a product inventory.
        :param instance: Instance of Magento
        :param auto_apply: Stock Validation confirmation
        :param m_locations: Magento products object
        :return: True
        """
        quant = self.env["stock.quant"]
        log = self.env["common.log.book.ept"]
        if instance.is_import_product_stock:
            consumable = []
            for m_location in m_locations:
                warehouse = m_location.import_stock_warehouse
                location = warehouse and warehouse.lot_stock_id
                if location:
                    search_criteria = create_search_criteria({"source_code": m_location.magento_location_code})
                    query_string = Php.http_build_query(search_criteria)
                    api_url = f"/V1/inventory/source-items?{query_string}"
                    response = req(instance, api_url)
                    stock_data = self.prepare_import_stock_dict(response, instance)
                    name = f'Inventory For Instance "{instance.name}" And Magento Location ' f'"{warehouse.name}"'
                    quant.create_inventory_adjustment_ept(stock_data.get("product_qty"), location, auto_apply, name)
                    consumable += stock_data.get("consumable")
                else:
                    raise UserError(_("Please Choose Import product stock location for {m_location.name}"))
            if consumable:
                model_id = self.env["common.log.lines.ept"].get_model_id("stock.quant")
                log = log.create_common_log_book("import", "magento_instance_id", instance, model_id, "magento_ept")
                self.create_consumable_products_log(consumable, log)
        return log

    def prepare_import_stock_dict(self, response, instance):
        """
        Prepare dictionary for import product stock from response.
        :param response: response received from Magento
        :param instance: Magento Instance object
        :param consumable: Dictionary of consumable products
        :param product_qty: Dictionary for import product stock
        :return: stock_to_import, consumable_products
        """
        consumable, product_qty = [], {}
        items = response.get("items", [])
        for item in items:
            m_product = self.search_magento_product(instance, item)
            if m_product:
                if instance.is_multi_warehouse_in_magento:
                    qty = item.get("quantity", 0) or 0
                else:
                    qty = item.get("qty", 0) or 0
                if qty > 0 and m_product.odoo_product_id.type == "product":
                    product_qty.update({m_product.odoo_product_id.id: qty})
                elif m_product.odoo_product_id.type != "product":
                    consumable.append(m_product.odoo_product_id.default_code)
        return {"consumable": consumable, "product_qty": product_qty}

    def search_magento_product(self, instance, item):
        """Create product search domain and search magento product
        :param: instance : instance object
        :param: item : item dict
        return product search domain"""
        domain = [("magento_instance_id", "=", instance.id), ("magento_website_ids", "!=", False)]
        if instance.is_multi_warehouse_in_magento:
            domain.append(("magento_sku", "=", item.get("sku", "") or ""))
        else:
            domain.append(("magento_product_id", "=", item.get("product_id", 0) or 0))
        return self.search(domain, limit=1)

    @staticmethod
    def create_consumable_products_log(consumable_products, log):
        """
        Generate process log for import product stock with consumable product.
        :param consumable_products: dictionary of consumable products
        :param log: common log book object
        """
        if consumable_products:
            message = f"""
            The following products have not been imported due to
            product type is other than 'Storable.'\n {str(list(set(consumable_products)))}
            """
            log.write({"log_lines": [(0, 0, {"message": message})]})

    @staticmethod
    def create_export_product_process_log(consumable, log):
        """
        Generate process log for export product stock with consumable product.
        :param consumable: dictionary of consumable products
        :param log: common log book object
        """
        if consumable:
            message = f"""
            The following products have not been exported due to
            product type is other than 'Storable.'\n {str(list(set(consumable)))}
            """
            log.write({"log_lines": [(0, 0, {"message": message})]})

    def exp_prd_stock_in_batches(self, stock_data, instance, api_url, data_key, method, job):
        """
        Export product stock in a bunch of 100 items.
        :param stock_data: dictionary for stock data
        :param instance: magento instance object
        :param api_url: export stock API url
        :param data_key: API dictionary key
        :param method: API method
        :param job: common log book object
        :return: common log book object
        """
        batch_size = 0
        for batch in range(0, len(stock_data) + 1, instance.batch_size):
            batch_size += instance.batch_size
            data = {data_key: stock_data[batch:batch_size]}
            _logger.info(f"Exporting Product Stock Batch {batch}")
            _logger.info(f"Product Stock Batch Data {data}")
            job = self.call_export_product_stock_api(instance, api_url, data, job, method)
        return job

    @staticmethod
    def call_export_product_stock_api(instance, api_url, data, log, method):
        """
        Call export product stock API for single or multi tracking inventory.
        :param instance: Magento instance object
        :param api_url: API Call URL
        :param data: Dictionary to be passed.
        :param log: Common log book object
        :param method: Api Request Method type (PUT/POST)
        :return: common log book object
        """
        try:
            responses = req(instance=instance, path=api_url, method=method, data=data)
        except Exception as error:
            raise UserError(_("Error while Export product stock " + str(error)))
        if responses:
            messages = []
            for response in responses:
                if isinstance(response, dict) and response.get("code") != "200":
                    messages.append((0, 0, {"message": response.get("message")}))
            if messages:
                log.write({"log_lines": messages})
        return True

    def get_magento_product_stock_ept(self, instance, product_ids, warehouse):
        """
        This Method relocates check type of stock.
        :param instance: This arguments relocates instance of amazon.
        :param product_ids: This arguments product listing id of odoo.
        :param warehouse:This arguments relocates warehouse of amazon.
        :return: This Method return product listing stock.
        """
        product = self.env["product.product"]
        stock = {}
        if product_ids:
            if instance.magento_stock_field == "free_qty":
                stock = product.get_free_qty_ept(warehouse, product_ids)
            elif instance.magento_stock_field == "virtual_available":
                stock = product.get_forecasted_qty_ept(warehouse, product_ids)
            elif instance.magento_stock_field == "onhand_qty":
                stock = product.get_onhand_qty_ept(warehouse, product_ids)
        return stock
