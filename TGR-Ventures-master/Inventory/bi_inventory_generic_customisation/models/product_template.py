from odoo import fields, models, api, _
from datetime import datetime, timedelta
import json
import requests
import time
from odoo.exceptions import UserError


ACCOUNT_DOMAIN = "['&', '&', '&', ('deprecated', '=', False), ('internal_type','=','other'), ('company_id', '=', current_company_id), ('is_off_balance', '=', False)]"


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_default_warehouse(self):
        """
        This method is used to set the default warehouse (Malaga) for tiger uno company.
        """
        warehouse = False
        if self.env.company.id == 10:
            warehouse = self.env["stock.warehouse"].search(
                [("id", "=", 17)],
                limit=1,
            )
        return warehouse if warehouse else False

    def _get_default_account(self):
        """
        This method is used to set the default account.
        """
        account = False
        if self.env.company.id == 10 or self.env.company.id == 9:
            account = self.env["account.account"].search(
                [("id", "=", 1549)],
                limit=1,
            )
        return account if account else False

    product_new_type = fields.Selection(
        [
            ("finished", "Finished Good"),
            ("component", "Component Part"),
            ("subassembly", "Subassembly"),
            ("nonstock", "Non-Stock Item"),
        ],
        "Type",
        default="finished",
    )
    sale_uom_id = fields.Many2one("uom.uom", string="Sale UOM")
    pack_size_desc = fields.Char(string="Pack Size Description")
    flower_type_id = fields.Many2one("flower.type", string="Flower Type Description")
    product_breeder_id = fields.Many2one("product.breeder", string="Brand Description", tracking=True)
    product_sex_id = fields.Many2one("product.sex", string="Sex Description")
    product_size_id = fields.Many2one("product.size", string="Product Size")
    retail_uk_price = fields.Float("Retail GBP", tracking=True)
    retail_us_price = fields.Float("Retail USD", tracking=True)
    retail_default_price = fields.Float("Retail Default EUR", tracking=True)
    retail_special_price = fields.Float("Retail Special EUR", tracking=True)
    wholesale_special_price = fields.Float("Wsale Special EUR", tracking=True)
    za_price = fields.Float("ZA Price", tracking=True)
    wholesale_special_us = fields.Float("Wsale Special USD", tracking=True)
    wholesale_special_za = fields.Float("Wsale Special ZAR", tracking=True)
    wholesale_special_uk = fields.Float("Wsale Special GBP", tracking=True)
    wholesale_us = fields.Float("Wsale USD", tracking=True)
    wholesale_za = fields.Float("Wsale ZAR", tracking=True)
    wholesale_uk = fields.Float("Wsale GBP", tracking=True)
    retail_special_us = fields.Float("Retail Special USD", tracking=True)
    retail_special_za = fields.Float("Retail Special ZAR", tracking=True)
    retail_special_uk = fields.Float("Retail Special GBP", tracking=True)
    retail_za_price = fields.Float("Retail ZAR", tracking=True)
    dimension = fields.Char(string="Dimension")

    # OVERRIDE TO CHANGE LABEL
    standard_price = fields.Float(
        "Cost",
        compute="_compute_standard_price",
        inverse="_set_standard_price",
        search="_search_standard_price",
        digits=(12, 3),
        groups="base.group_user",
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the next unit that will leave the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""",
        tracking=True,
    )
    last_cost = fields.Float("Cost(No need/Unused)", digits=(12, 3), tracking=True)
    min_cost = fields.Float("Min Cost", tracking=True)
    max_cost = fields.Float("Max Cost", tracking=True)
    item_status = fields.Selection(
        [("active", "Active"), ("in_active", "In Active"), ("delete", "Marked for Deletion")], string="Item Status"
    )
    default_warehouse_id = fields.Many2one(
        "stock.warehouse", string="Default Warehouse", default=_get_default_warehouse
    )
    account_inventory_id = fields.Many2one("account.account", string="Inventory Account")
    account_sub_inventory_id = fields.Many2one("account.analytic.account", string="Inventory Sub.")
    account_reason_subcode_id = fields.Many2one("account.analytic.account", string="Reason Code Sub.")
    account_sub_sales_id = fields.Many2one("account.analytic.account", string="Sales Sub.")
    account_cogs_id = fields.Many2one("account.account", string="COGS Account")
    account_cogs_sub_id = fields.Many2one("account.analytic.account", string="COGS Sub.")
    account_standard_cost_variance_id = fields.Many2one("account.account", string="Standard Cost Variance Account")
    account_standard_cost_sub_variance_id = fields.Many2one(
        "account.analytic.account", string="Standard Cost Variance Sub."
    )
    account_standard_cost_revaluation_id = fields.Many2one(
        "account.account", string="Standard Cost Revaluation Account"
    )
    account_standard_cost_sub_revaluation_id = fields.Many2one(
        "account.analytic.account", string="Standard Cost Revaluation Sub"
    )
    account_po_sub_accrual = fields.Many2one("account.analytic.account", string="PO Accrual Sub.")
    account_purchase_price_variance_id = fields.Many2one(
        "account.account", string="Purchase Price Variance Account", default=_get_default_account
    )
    account_purchase_price_sub_variance_id = fields.Many2one(
        "account.analytic.account", string="Purchase Price Variance Sub."
    )
    property_account_expense_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Expense Account",
        domain=ACCOUNT_DOMAIN,
        default=_get_default_account,
        help="Keep this field empty to use the default value from the product category. If anglo-saxon accounting with automated valuation method is configured, the expense account on the product category will be used.",
    )
    account_landed_cost_variance_id = fields.Many2one("account.account", string="Landed Cost Variance Account")
    account_landed_cost_sub_variance_id = fields.Many2one("account.analytic.account", string="Landed Cost Variance Sub")
    case_quantity = fields.Integer(string="Case Quantity", tracking=True)
    attribute_product_line_ids = fields.One2many("product.attribute.line", "product_temp_id", string="Attribute Lines")
    check_color = fields.Boolean("check_color", compute="_compute_check_color", default=False)
    black_color = fields.Boolean("black_color", default=False)
    supplier_sku_no = fields.Char(string="Supplier SKU")
    malag_stock_quant = fields.Float(string="Malaga/Available", compute="_compute_malag_stock")
    uk_stock_quant = fields.Float(string="UK/Available", compute="_compute_uk_stock")
    bulk_uk_stock_quant = fields.Float(string="BULK UK/Stock", compute="_compute_uk_stock")
    bulk_es_stock_quant = fields.Float(string="BULK ES/Stock", compute="_compute_uk_stock")
    za_stock_quant = fields.Float(string="ZA/Stock", compute="_compute_uk_stock")
    wsale_stock_quant = fields.Float(string="WSALE/Stock", compute="_compute_uk_stock")
    uk_3pl_stock_quant = fields.Float(string="UK3PL/Available", compute="_compute_uk_stock")
    usit_stock_quant = fields.Float(string="USIT/Stock", compute="_compute_uk_stock")
    lost_stock_quant = fields.Float(string="Lost/Stock", compute="_compute_uk_stock")
    total_stock_quant = fields.Float(string="Available Qty", compute="_compute_uk_stock")
    tag_groups_ids = fields.Many2many("account.tax", string="Tax Category")
    pi_cycle = fields.Char(string="PI Cycle")
    wholesale_price_value = fields.Float("Wsale Default EUR", tracking=True)
    vendor_inventory_char = fields.Char("Vendor Inventory ID")
    lead_time_day = fields.Char("Lead Time (Days)")
    pa_accural_account = fields.Many2one("account.account", string="PO Accrual Account")
    out_of_stock_date = fields.Date("Out Of Stock Date")
    back_stock_date = fields.Date("Back in Stock Date")

    recently_created = fields.Boolean("Recently Created", default=False, copy=False)
    zero_onhand = fields.Boolean("field_name", default=False, copy=False)
    is_pn_us_two = fields.Boolean(string="T1 US", tracking=True)
    is_pn_us = fields.Boolean(string="PhytoNation", tracking=True)
    is_pn_br = fields.Boolean(string="PN BR", tracking=True)
    is_pn_sa = fields.Boolean(string="PN SA", tracking=True)
    is_out_of_stock = fields.Boolean(string="Out of Stock", tracking=True)
    is_back_in_stock = fields.Boolean(string="Back in Stock", tracking=True)

    is_exclude_from_replenishment = fields.Boolean(string="Exclude from Replenishment", tracking=True)
    is_excluded_pricelist = fields.Boolean("Exclude from Pricelist", tracking=True)
    is_excluded_customer = fields.Boolean("Exclude from customers", tracking=True)
    is_pending_discontinued = fields.Boolean("Pending Discontinued", tracking=True)
    website_instance_ids = fields.One2many("product.website.model", "product_website_id", string="Website Lines")
    is_website = fields.Boolean("Is website", default=False, compute="_compute_website_line")
    uk_tiger_one_boolean = fields.Boolean(string="UK Tiger One Enable/Disable", default=True, tracking=True)
    eu_tiger_one_boolean = fields.Boolean(string="EU Tiger One Enable/Disable", default=True, tracking=True)
    sa_tiger_one_boolean = fields.Boolean(string="SA Tiger One Enable/Disable", default=True, tracking=True)
    usa_tiger_one_boolean = fields.Boolean(string="USA Tiger One Enable/Disable", default=True, tracking=True)
    uk_seedsman_boolean = fields.Boolean(string="UK Seedsman Enable/Disable", default=True, tracking=True)
    eu_seedsman_boolean = fields.Boolean(string="EU Seedsman Enable/Disable", default=True, tracking=True)
    sa_seedsman_boolean = fields.Boolean(string="SA Seedsman Enable/Disable", default=True, tracking=True)
    usa_seedsman_boolean = fields.Boolean(string="USA Seedsman Enable/Disable", default=True, tracking=True)
    uk_eztestkits_boolean = fields.Boolean(string="UK Eztestkits Enable/Disable", default=True, tracking=True)
    eu_eztestkits_boolean = fields.Boolean(string="EU Eztestkits Enable/Disable", default=True, tracking=True)
    sa_eztestkits_boolean = fields.Boolean(string="SA Eztestkits Enable/Disable", default=True, tracking=True)
    usa_eztestkits_boolean = fields.Boolean(string="USA Eztestkits Enable/Disable", default=True, tracking=True)
    pytho_n_boolean = fields.Boolean(string="Pytho N Enable/Disable", default=True, tracking=True)
    product_tag_ids = fields.Many2many("product.tag", string="Product Tag", tracking=True)
    live_stock = fields.Float(string="LIVE/Stock", compute="_compute_us_stock")
    live_stock_available = fields.Float(string="LIVE/Stock Available", compute="_compute_us_stock")
    whusa_stock = fields.Float(string="WHUSA/Stock", compute="_compute_us_stock")
    unpac_stock = fields.Float(string="UNPAC/Stock", compute="_compute_us_stock")
    phyto_stock = fields.Float(string="Phyto/Stock", compute="_compute_phyto_stock")
    malag_on_hand_quant = fields.Float(string="Malaga/On hand", compute="_compute_malag_stock")
    uk_on_hand_quant = fields.Float(string="UK/On hand", compute="_compute_uk_stock")
    uk_3pl_on_hand_quant = fields.Float(string="UK3PL/On hand", compute="_compute_uk_stock")
    qty_expected = fields.Float("Expected Qty", compute="_compute_qty_expected")
    is_usa_replenishment = fields.Boolean("USA Replenishment Enable", default=False)
    is_malaga_replenishment = fields.Boolean("MALAGA Replenishment Enable", default=False)
    is_uk_replenishment = fields.Boolean("UK Replenishment Enable", default=False)
    categ_id = fields.Many2one(tracking=True)
    default_code = fields.Char(tracking=True)
    barcode = fields.Char(tracking=True)
    last_purchase_order_id = fields.Many2one("purchase.order", string="Last Purchase Order", company_dependent=True)
    is_free_product = fields.Boolean(string="Free Products", default=False, copy=False)
    date_of_receipt = fields.Datetime(string="Date of Receipt", compute="_compute_date_of_receipt")
    is_last_purchase_order = fields.Boolean(string="Is Last Purchase Order", compute="_compute_is_last_purchase_order")

    bules_stock = fields.Float(string="BULES/Stock", compute="_compute_eu_and_uk_stock")
    buluk_stock = fields.Float(string="BULUK/Stock", compute="_compute_eu_and_uk_stock")
    escdo_stock = fields.Float(string="ESCDO/Stock", compute="_compute_eu_and_uk_stock")
    wsale_stock = fields.Float(string="WSALE/Stock", compute="_compute_eu_and_uk_stock")

    lost_stock = fields.Float(string="LOST/Stock", compute="_compute_eu_and_uk_stock")
    malag_stock = fields.Float(string="MALAG/Stock", compute="_compute_eu_and_uk_stock")
    uk3pl_stock = fields.Float(string="UK3PL/Stock", compute="_compute_eu_and_uk_stock")
    ukbar_stock = fields.Float(string="UKBAR/Stock", compute="_compute_eu_and_uk_stock")

    ukcdo_stock = fields.Float(string="UKCDO/Stock", compute="_compute_eu_and_uk_stock")
    ukwsa_stock = fields.Float(string="UKWSA/Stock", compute="_compute_eu_and_uk_stock")
    usit_stock = fields.Float(string="USIT/Stock", compute="_compute_eu_and_uk_stock")
    zacdo_stock = fields.Float(string="ZACDO/Stock", compute="_compute_eu_and_uk_stock")
    zates_stock = fields.Float(string="ZATES/Stock", compute="_compute_eu_and_uk_stock")
    zawsa_stock = fields.Float(string="ZAWSA/Stock", compute="_compute_eu_and_uk_stock")
    previous_last_cost = fields.Monetary(string="Previous Last Cost", default=0.00)
    last_cost_2 = fields.Float('Last Cost', company_dependent=True)
    is_not_product_cost_manager = fields.Boolean(compute="_compute_is_not_product_cost_manager")


    def _compute_is_not_product_cost_manager(self):
        for rec in self:
            rec.is_not_product_cost_manager = True if not self.env.user.has_group("bi_inventory_generic_customisation.product_cost_security") else False

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
                            "sku": self.default_code,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "eu_tiger_one_boolean":
                store_code = "tigerone_eu_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.default_code,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "sa_tiger_one_boolean":
                store_code = "tigerone_sa_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.default_code,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "usa_tiger_one_boolean":
                store_code = "tigerone_us_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.default_code,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "uk_seedsman_boolean":
                store_code = "uk"
                data = [
                    {
                        "product": {
                            "sku": self.default_code,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "eu_seedsman_boolean":
                store_code = "eu"
                data = [
                    {
                        "product": {
                            "sku": self.default_code,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "sa_seedsman_boolean":
                store_code = "za"
                data = [
                    {
                        "product": {
                            "sku": self.default_code,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "usa_seedsman_boolean":
                store_code = "us"
                data = [
                    {
                        "product": {
                            "sku": self.default_code,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "uk_eztestkits_boolean":
                store_code = "eztestkits_uk_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.default_code,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "eu_eztestkits_boolean":
                store_code = "eztestkits_eu_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.default_code,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "sa_eztestkits_boolean":
                store_code = "eztestkits_sa_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.default_code,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "usa_eztestkits_boolean":
                store_code = "eztestkits_usa_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.default_code,
                            "status": 1 if vals.get(rf) else 2,
                        }
                    }
                ]
            elif rf == "pytho_n_boolean":
                store_code = "pytho_nation_store_view"
                data = [
                    {
                        "product": {
                            "sku": self.default_code,
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
        if "active" in vals:
            vals["eu_tiger_one_boolean"] = False if not vals.get("active") else True
            vals["usa_tiger_one_boolean"] = False if not vals.get("active") else True
            vals["uk_tiger_one_boolean"] = False if not vals.get("active") else True
            vals["sa_tiger_one_boolean"] = False if not vals.get("active") else True
            for rec in self:
                vals['previous_last_cost'] = rec.standard_price

        if "product_tag_ids" in vals:
            if isinstance(vals["product_tag_ids"][0], tuple):  # Updation through Update Product Other Details Wizard
                for tag in vals["product_tag_ids"][0][1:]:
                    new_tag = self.env["product.tag"].search([("id", "=", tag)])
                    if tag not in self.product_tag_ids.ids:
                        if vals["product_tag_ids"][0][0] == 4:  # Checks if Tag is being added through Wizard
                            self.message_post(body=_("Product Tag :  Added  [{}] to tags".format(new_tag.name)))
                    else:
                        if vals["product_tag_ids"][0][0] == 3:  # Checks if Tag is being removed through Wizard
                            self.message_post(body=_("Product Tag :  Removed [{}] from tags".format(new_tag.name)))
            elif isinstance(vals["product_tag_ids"][0][2], list):  # Updation through Product form
                old_tags = " ".join(["[" + tag.name + "]" for tag in self.product_tag_ids])
                new_tags = self.env["product.tag"].search([("id", "in", vals["product_tag_ids"][0][2])])
                new_tags_list = " ".join(["[" + tag.name + "]" for tag in new_tags])
                self.message_post(
                    body=_(
                        "Product Tag :  {} ===> {}".format(
                            old_tags if old_tags != "" else "Empty", new_tags_list if new_tags_list != "" else "Empty"
                        )
                    )
                )

        return super(ProductTemplate, self).write(vals)
    
    # @api.onchange("last_cost_2")
    # def _onchange_last_cost_2(self):
    #     resource = f"product.product,{self.product_variant_id.id}"
    #     companies = (
    #         self.env["res.company"]
    #         .sudo()
    #         .search([("synchronize_product_price", "=", True), ("id", "!=", self.env.company.id)])
    #     )
    #     if companies:
    #         company_ids = companies.ids
    #         if len(companies) == 1:
    #             domain = f"company_id={companies.ids[0]}"
    #         else:
    #             domain = f"company_id in {tuple(companies.ids)}"
            # get_property_query = (
            #     f"""SELECT id FROM ir_property WHERE name='last_cost_2' AND res_id='{resource}' AND {domain}"""
            # )
            # self.env.cr.execute(get_property_query)
            # property_query_result = self.env.cr.dictfetchall()
            # required_properties = [property["id"] for property in property_query_result]
    #         for property in required_properties:
    #             get_this_property_company = f"""SELECT company_id FROM ir_property WHERE id={property}"""
    #             self.env.cr.execute(get_this_property_company)
    #             result_company = self.env.cr.dictfetchall()
    #             property_update_query = (
    #                 f"""UPDATE ir_property SET value_float={self.last_cost_2} WHERE id={property}"""
    #             )
    #             self.env.cr.execute(property_update_query)
    #             company_ids.remove(result_company[0]["company_id"])
    #         model_id = self.env["ir.model"].sudo().search([("model", "=", "product.product")], limit=1)
    #         field_id = (
    #             self.env["ir.model.fields"]
    #             .sudo()
    #             .search(
    #                 [
    #                     ("name", "=", "last_cost_2"),
    #                     ("field_description", "=", "Last Cost"),
    #                     ("model_id", "=", model_id.id),
    #                 ],
    #                 limit=1,
    #             )
    #         )
    #         for company in company_ids:
    #             vals = {
    #                 "company_id": company,
    #                 "res_id": resource,
    #                 "value_float": self.last_cost_2,
    #                 "name": "last_cost_2",
    #                 "fields_id": field_id.id,
    #             }
    #             self.env["ir.property"].sudo().create(vals)

    @api.depends("name")
    def _compute_check_color(self):
        for each in self:
            if each.qty_available == 0:
                each.check_color = False
                each.zero_onhand = True
            else:
                each.check_color = True
                each.zero_onhand = False

            product_days = (
                self.env["ir.config_parameter"].sudo().get_param("bi_inventory_generic_customisation.product_days")
            )
            date_created = each.create_date + timedelta(days=int(product_days))
            if date_created.date() >= datetime.now().date():
                each.check_color = True
                each.recently_created = True

            elif date_created.date() <= datetime.now().date():
                each.black_color = True
                each.check_color = False
                each.recently_created = False

    @api.onchange("name", "product_breeder_id")
    def _onchange_product_track(self):
        for each in self:
            if each.product_breeder_id:
                each.tracking = each.product_breeder_id.tracking

    def action_trigger_pending_discontinued(self):
        products = self.env["product.template"].sudo().search([("is_pending_discontinued", "=", True)])
        for each in products:
            quantity = each.qty_available
            if each.is_pending_discontinued and quantity == 0.0:
                each.active = False
            else:
                each.active = True

    def action_trigger_back_in_stock(self):
        products = self.env["product.template"].search([("is_back_in_stock", "=", True)])
        for each in products:
            if each.back_stock_date == datetime.today().date():
                each.is_out_of_stock = False

    def _compute_malag_stock(self):
        for each in self:
            quantity_malag = 0
            malag_on_hand_quant = 0
            product_id = self.env["product.product"].search([("product_tmpl_id", "=", each.id)], limit=1)
            if self.env["stock.location"].search([("id", "=", 144)]):
                quantity_malag = product_id.with_context({"location": 144}).free_qty
                malag_on_hand_quant = product_id.with_context({"location": 144}).qty_available
            each.malag_stock_quant = quantity_malag
            each.malag_on_hand_quant = malag_on_hand_quant

    def _compute_uk_stock(self):
        for each in self:
            quantity_uk = 0
            quantity_bulk_uk = 0
            quantity_bulk_es = 0
            quantity_za = 0
            quantity_wsale = 0
            quantity_uk_3pl = 0
            quantity_usit_stock_quant = 0
            lost_stock_quant = 0
            total_stock_quant = 0
            uk_on_hand_quant = 0
            uk_3pl_on_hand_quant = 0
            product_id = self.env["product.product"].search([("product_tmpl_id", "=", each.id)], limit=1)
            if self.env["stock.location"].search([("id", "=", 132)]):
                quantity_uk = product_id.with_context({"location": 132}).free_qty
                uk_on_hand_quant = product_id.with_context({"location": 132}).qty_available
            each.uk_stock_quant = quantity_uk
            if self.env["stock.location"].search([("id", "=", 162)]):
                quantity_bulk_uk = product_id.with_context({"location": 162}).qty_available
            if self.env["stock.location"].search([("id", "=", 156)]):
                quantity_bulk_es = product_id.with_context({"location": 156}).qty_available
            if self.env["stock.location"].search([("id", "=", 150)]):
                quantity_za = product_id.with_context({"location": 150}).qty_available
            if self.env["stock.location"].search([("id", "=", 168)]):
                quantity_wsale = product_id.with_context({"location": 168}).qty_available
            if self.env["stock.location"].search([("id", "=", 138)]):
                quantity_uk_3pl = product_id.with_context({"location": 138}).free_qty
                uk_3pl_on_hand_quant = product_id.with_context({"location": 138}).qty_available
            if self.env["stock.location"].search([("id", "=", 174)]):
                quantity_usit_stock_quant = product_id.with_context({"location": 174}).qty_available
            if self.env["stock.location"].search([("id", "=", 180)]):
                lost_stock_quant = product_id.with_context({"location": 180}).qty_available
            total_stock_quant = product_id.with_context().free_qty
            each.bulk_uk_stock_quant = quantity_bulk_uk
            each.uk_on_hand_quant = uk_on_hand_quant
            each.bulk_es_stock_quant = quantity_bulk_es
            each.za_stock_quant = quantity_za
            each.wsale_stock_quant = quantity_wsale
            each.uk_3pl_stock_quant = quantity_uk_3pl
            each.usit_stock_quant = quantity_usit_stock_quant
            each.lost_stock_quant = lost_stock_quant
            each.total_stock_quant = total_stock_quant
            each.uk_3pl_on_hand_quant = uk_3pl_on_hand_quant

    def _compute_us_stock(self):
        for each in self:
            live_stock = 0
            live_stock_available = 0
            whusa_stock = 0
            unpac_stock = 0
            product_id = self.env["product.product"].search([("product_tmpl_id", "=", each.id)], limit=1)
            if self.env["stock.location"].search([("id", "=", 190)]):
                live_stock = product_id.with_context({"location": 190}).qty_available
            if self.env["stock.location"].search([("id", "=", 190)]):
                live_stock_available = product_id.with_context({"location": 190}).free_qty
            if self.env["stock.location"].search([("id", "=", 196)]):
                whusa_stock = product_id.with_context({"location": 196}).qty_available
            if self.env["stock.location"].search([("id", "=", 202)]):
                unpac_stock = product_id.with_context({"location": 202}).qty_available
            each.live_stock = live_stock
            each.live_stock_available = live_stock_available
            each.whusa_stock = whusa_stock
            each.unpac_stock = unpac_stock

    def _compute_phyto_stock(self):
        for each in self:
            phyto_stock = 0
            product_id = self.env["product.product"].search([("product_tmpl_id", "=", each.id)], limit=1)
            if self.env["stock.location"].search([("id", "=", 92)]):
                phyto_stock = product_id.with_context({"location": 92}).qty_available
            each.phyto_stock = phyto_stock

    @api.model
    def default_get(self, fields):
        result = super(ProductTemplate, self).default_get(fields)
        if self.env.user.has_group("odoo_magento2_ept.group_magento_manager_ept"):
            website_ids = self.env["magento.website"].search([])
            line_value = []
            for line in website_ids:
                line_value.append((0, 0, {"website_instance_id": line.id}))
            if line_value:
                result.update(
                    {
                        "website_instance_ids": line_value,
                    }
                )
        return result

    def _compute_website_line(self):
        self.is_website = True
        website_ids = self.env["magento.website"].search([])
        line_value = []
        if not self.website_instance_ids:
            for line in website_ids:
                price = 0
                if line.name == "Tiger One UK":
                    price = self.wholesale_uk
                elif line.name == "Tiger One EU":
                    price = self.wholesale_price_value
                elif line.name == "Tiger One SA":
                    price = self.wholesale_za
                elif line.name == "Seedsman UK":
                    price = self.retail_uk_price
                elif line.name == "Seedsman USA":
                    price = self.retail_us_price
                elif line.name == "Seedsman EU":
                    price = self.retail_default_price
                elif line.name == "Seedsman SA":
                    price = self.retail_za_price
                elif line.name == "Tiger One USA":
                    price = self.wholesale_us
                line_value.append(
                    (
                        0,
                        0,
                        {
                            "website_instance_id": line.id,
                            "price_unit": price,
                        },
                    )
                )
            if line_value:
                self.update(
                    {
                        "website_instance_ids": line_value,
                    }
                )
        if self.website_instance_ids:
            for line in self.website_instance_ids:
                if line.website_instance_id.name == "Tiger One UK":
                    if self.wholesale_price_value:
                        line.price_unit = self.wholesale_price_value
                elif line.website_instance_id.name == "Tiger One EU":
                    if self.wholesale_price_value:
                        line.price_unit = self.wholesale_price_value
                elif line.website_instance_id.name == "Tiger One SA":
                    if self.wholesale_za:
                        line.price_unit = self.wholesale_za
                elif line.website_instance_id.name == "Seedsman UK":
                    if self.retail_uk_price:
                        line.price_unit = self.retail_uk_price
                elif line.website_instance_id.name == "Seedsman USA":
                    if self.retail_us_price:
                        line.price_unit = self.retail_us_price
                elif line.website_instance_id.name == "Seedsman EU":
                    if self.retail_default_price:
                        line.price_unit = self.retail_default_price
                elif line.website_instance_id.name == "Seedsman SA":
                    if self.retail_za_price:
                        line.price_unit = self.retail_za_price
                elif line.website_instance_id.name == "Tiger One USA":
                    if self.wholesale_us:
                        line.price_unit = self.wholesale_us

    def action_update_product_enable_disable(self):
        return {
            "name": _("Enable/Disable"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "update.product.disable",
            "context": {},
            "target": "new",
        }

    # _sql_constraints = [
    #     ("default_code_unique", "unique(default_code)", "Default code already exists."),
    # ]

    def update_product_price_cron(self, magento_website_id=False):
        instance = self.env["magento.instance"].sudo().search([], limit=1)
        instance_url = instance.magento_url
        headers = self.get_headers(instance.access_token)
        if not magento_website_id:
            raise UserError(_("No website found with the given magento ID."))
        website = self.env["magento.website"].browse(magento_website_id)
        products = self.env["product.template"].search([("default_code", "!=", False)])
        log_book = self.env["common.log.book.ept"].search([], limit=1)
        if not log_book:
            log_book = self.env["common.log.book.ept"].create({})
        store_id = self.env["magento.storeview"].search([("magento_website_id", "=", magento_website_id)], limit=1)
        api_url = f"{instance_url}/rest/{store_id.magento_storeview_code}/async/bulk/V1/products"
        product_data = []
        for product in products:
            status = 1
            if store_id.magento_storeview_code == "tigerone_uk_store_view":
                status = 1 if product.uk_tiger_one_boolean else 2
            elif store_id.magento_storeview_code == "tigerone_eu_store_view":
                status = 1 if product.eu_tiger_one_boolean else 2
            elif store_id.magento_storeview_code == "tigerone_sa_store_view":
                status = 1 if product.sa_tiger_one_boolean else 2
            elif store_id.magento_storeview_code == "tigerone_us_store_view":
                status = 1 if product.usa_tiger_one_boolean else 2
            elif store_id.magento_storeview_code == "uk":
                status = 1 if product.uk_seedsman_boolean else 2
            elif store_id.magento_storeview_code == "us":
                status = 1 if product.usa_seedsman_boolean else 2
            elif store_id.magento_storeview_code == "eu":
                status = 1 if product.eu_seedsman_boolean else 2
            elif store_id.magento_storeview_code == "za":
                status = 1 if product.sa_seedsman_boolean else 2
            elif store_id.magento_storeview_code == "eztestkits_uk_store_view":
                status = 1 if product.uk_eztestkits_boolean else 2
            elif store_id.magento_storeview_code == "eztestkits_eu_store_view":
                status = 1 if product.eu_eztestkits_boolean else 2
            elif store_id.magento_storeview_code == "eztestkits_sa_store_view":
                status = 1 if product.sa_eztestkits_boolean else 2
            elif store_id.magento_storeview_code == "eztestkits_usa_store_view":
                status = 1 if product.usa_eztestkits_boolean else 2
            elif store_id.magento_storeview_code == "pytho_nation_store_view":
                status = 1 if product.pytho_n_boolean else 2
            price = product.website_instance_ids.filtered(lambda site: site.website_instance_id == website)
            product_data.append(
                {
                    "product": {
                        "sku": product.default_code,
                        "price": price[0].price_unit if price else 0,
                        "status": status,
                    }
                }
            )
        count = 5000
        subsets = (product_data[x : x + count] for x in range(0, len(product_data), count))
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
                                "api_data_sent": json.dumps(subset),
                            },
                        )
                    ]
                }
            )
            time.sleep(300)

    def get_headers(self, token):
        return {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "My User Agent 1.0",
            "Authorization": "Bearer {}".format(token),
        }

    def _compute_qty_expected(self):
        """
        compute function for expected qty field on template.
        """
        purchase_line_obj = self.env["purchase.order.line"]
        for template in self:
            template.qty_expected = 0
            po_lines = purchase_line_obj.search(
                [
                    ("product_id", "in", template.product_variant_id.ids),
                    ("qty_received", "=", 0),
                    ("product_qty", ">", 0),
                    ("order_id.state", "=", "purchase"),
                ]
            )
            if po_lines:
                template.qty_expected = sum((po_lines).mapped("product_qty"))

    def action_template_expected_qty(self):
        """
        action return expected qty view for template.
        """
        self.ensure_one()
        view = self.env.ref("bi_inventory_generic_customisation.purchase_order_line_tree_view").id
        purchase_line_obj = self.env["purchase.order.line"]
        po_lines = purchase_line_obj.search(
            [
                ("product_id", "in", self.product_variant_id.ids),
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

    @api.onchange("product_breeder_id")
    def _onchange_product_breeder(self):
        for each in self:
            if each.product_breeder_id:
                each.weight = each.product_breeder_id.weight
                each.dimension = each.product_breeder_id.dimension

    hs_code = fields.Char("HS Code")

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name}"
            result.append((record.id, name))
        return result

    def update_product_receipt_date(self):
        """
        cron function for update date of receipt for product template
        Returns:

        """
        for rec in self:
            if rec.last_purchase_order_id and rec.last_purchase_order_id.effective_date:
                rec.date_of_receipt = rec.last_purchase_order_id.effective_date

    def _compute_eu_and_uk_stock(self):
        for each in self:
            bules_stock = 0
            buluk_stock = 0
            escdo_stock = 0
            wsale_stock = 0
            lost_stock = 0
            malag_stock = 0
            uk3pl_stock = 0
            ukbar_stock = 0
            ukcdo_stock = 0
            ukwsa_stock = 0
            usit_stock = 0
            zacdo_stock = 0
            zates_stock = 0
            zawsa_stock = 0
            product_id = self.env["product.product"].search([("product_tmpl_id", "=", each.id)], limit=1)
            if self.env["stock.location"].search([("id", "=", 156)]):
                bules_stock = product_id.with_context({"location": 156}).qty_available or 0.00
            if self.env["stock.location"].search([("id", "=", 162)]):
                buluk_stock = product_id.with_context({"location": 162}).qty_available or 0.00
            if self.env["stock.location"].search([("id", "=", 364)]):
                escdo_stock = product_id.with_context({"location": 364}).qty_available or 0.00
            if self.env["stock.location"].search([("id", "=", 168)]):
                wsale_stock = product_id.with_context({"location": 168}).qty_available or 0.00

            if self.env["stock.location"].search([("id", "=", 180)]):
                lost_stock = product_id.with_context({"location": 180}).qty_available or 0.00
            if self.env["stock.location"].search([("id", "=", 144)]):
                malag_stock = product_id.with_context({"location": 144}).qty_available or 0.00
            if self.env["stock.location"].search([("id", "=", 138)]):
                uk3pl_stock = product_id.with_context({"location": 138}).qty_available or 0.00
            if self.env["stock.location"].search([("id", "=", 132)]):
                ukbar_stock = product_id.with_context({"location": 132}).qty_available or 0.00
            if self.env["stock.location"].search([("id", "=", 346)]):
                ukcdo_stock = product_id.with_context({"location": 346}).qty_available or 0.00
            if self.env["stock.location"].search([("id", "=", 298)]):
                ukwsa_stock = product_id.with_context({"location": 298}).qty_available or 0.00
            if self.env["stock.location"].search([("id", "=", 174)]):
                usit_stock = product_id.with_context({"location": 174}).qty_available or 0.00
            if self.env["stock.location"].search([("id", "=", 352)]):
                zacdo_stock = product_id.with_context({"location": 352}).qty_available or 0.00
            if self.env["stock.location"].search([("id", "=", 150)]):
                zates_stock = product_id.with_context({"location": 150}).qty_available or 0.00
            if self.env["stock.location"].search([("id", "=", 358)]):
                zawsa_stock = product_id.with_context({"location": 358}).qty_available or 0.00
            each.bules_stock = bules_stock
            each.buluk_stock = buluk_stock
            each.escdo_stock = escdo_stock
            each.wsale_stock = wsale_stock

            each.lost_stock = lost_stock
            each.malag_stock = malag_stock
            each.uk3pl_stock = uk3pl_stock
            each.ukbar_stock = ukbar_stock
            each.ukcdo_stock = ukcdo_stock
            each.ukwsa_stock = ukwsa_stock
            each.usit_stock = usit_stock
            each.zacdo_stock = zacdo_stock
            each.zates_stock = zates_stock
            each.zawsa_stock = zawsa_stock

    def _compute_is_last_purchase_order(self):
        self.is_last_purchase_order = False
        for rec in self:
            purchase_order = (
                self.env["purchase.order.line"]
                .search([("product_id.product_tmpl_id", "=", rec.id)])
                .mapped("order_id")
                .filtered(lambda p: p.state == "purchase")
            )
            po_id_list = []
            for order in purchase_order:
                if order.picking_ids.filtered(lambda x: x.state == "done"):
                    po_id_list.append(order)
            if po_id_list:
                rec.last_purchase_order_id = po_id_list[0].id

    @api.depends("last_purchase_order_id")
    def _compute_date_of_receipt(self):
        for rec in self:
            rec.date_of_receipt = False
            if rec.last_purchase_order_id and rec.last_purchase_order_id.company_id.id == self.env.company.id:
                rec.date_of_receipt = rec.last_purchase_order_id.effective_date


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_new_type = fields.Selection(
        [("finished", "Finished Good"), ("component", "Component Part"), ("subassembly", "Subassembly")],
        "Product Type",
        default="finished",
    )
    sale_uom_id = fields.Many2one("uom.uom", string="Sale UOM")
    pack_size_desc = fields.Char(string="Pack Size Description", related="product_tmpl_id.pack_size_desc")
    flower_type_id = fields.Many2one("flower.type", string="Flower Type", related="product_tmpl_id.flower_type_id")
    product_breeder_id = fields.Many2one(
        "product.breeder", string="Product Brand", related="product_tmpl_id.product_breeder_id"
    )
    product_sex_id = fields.Many2one("product.sex", string="Product Sex", related="product_tmpl_id.product_sex_id")
    product_size_id = fields.Many2one("product.size", string="Product Size")
    account_inventory_id = fields.Many2one("account.account", string="Inventory Account")
    account_sub_inventory_id = fields.Many2one("account.analytic.account", string="Inventory Sub.")
    account_reason_subcode_id = fields.Many2one("account.analytic.account", string="Reason Code Sub.")
    account_sub_sales_id = fields.Many2one("account.analytic.account", string="Sales Sub.")
    account_cogs_id = fields.Many2one("account.account", string="COGS Account")
    account_cogs_sub_id = fields.Many2one("account.analytic.account", string="COGS Sub.")
    account_standard_cost_variance_id = fields.Many2one("account.account", string="Standard Cost Variance Account")
    account_standard_cost_sub_variance_id = fields.Many2one(
        "account.analytic.account", string="Standard Cost Variance Sub."
    )
    account_standard_cost_revaluation_id = fields.Many2one(
        "account.account", string="Standard Cost Revaluation Account"
    )
    account_standard_cost_sub_revaluation_id = fields.Many2one(
        "account.analytic.account", string="Standard Cost Revaluation Sub"
    )
    account_po_sub_accrual = fields.Many2one("account.analytic.account", string="PO Accrual Sub.")
    account_purchase_price_variance_id = fields.Many2one("account.account", string="Purchase Price Variance Account")
    account_purchase_price_sub_variance_id = fields.Many2one(
        "account.analytic.account", string="Purchase Price Variance Sub."
    )
    account_landed_cost_variance_id = fields.Many2one("account.account", string="Landed Cost Variance Account")
    account_landed_cost_sub_variance_id = fields.Many2one("account.analytic.account", string="Landed Cost Variance Sub")

    @api.onchange("name", "product_breeder_id")
    def _onchange_product_track(self):
        for each in self:
            if each.product_breeder_id:
                each.tracking = each.product_tmpl_id.product_breeder_id.tracking

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name}"
            result.append((record.id, name))
        return result


class ProductAttributeLine(models.Model):
    _name = "product.attribute.line"

    product_temp_id = fields.Many2one("product.template", string="Attribute ID")
    product_attribute = fields.Many2one("product.attribute.model", string="Attribute")
    required_boolean = fields.Boolean(string="Required")
    value_boolean = fields.Boolean(string="Value")
    date_attribute = fields.Date(string="Date")


class ProductWebsiteModel(models.Model):
    _name = "product.website.model"

    product_website_id = fields.Many2one("product.template", string="Website ID")
    website_instance_id = fields.Many2one("magento.website", string="Website")
    enable_disable_product = fields.Selection(
        string="Enable/Disable", selection=[("enable", "Enable"), ("disable", "Disable")]
    )
    price_unit = fields.Float(string="Price Unit")
