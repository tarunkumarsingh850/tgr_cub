from odoo import models, fields, _
import base64
import xlrd
from odoo.exceptions import UserError
from odoo.http import request
import requests
import json


class ProductWebsiteExport(models.TransientModel):
    _name = "product.website.export.import"
    _description = "Product Website Export"

    magento_website_id = fields.Many2one("magento.website", string="Magento Website")
    excel_file = fields.Binary(
        "Upload Excel",
        attachment=True,
    )
    product_type = fields.Selection(
        string="Product Type", selection=[("configurable", "Configurable"), ("simple", "Simple")], required=1
    )

    def export_template(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "ids": self.ids,
                "magento_website_id": self.magento_website_id.id,
            },
        }
        return self.env.ref("bi_export_product_enable_website.action_export_template").report_action(
            self, data=data, config=False
        )

    def export_simple_template(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "ids": self.ids,
            },
        }
        return self.env.ref("bi_export_product_enable_website.action_export_simple_template").report_action(
            self, data=data, config=False
        )

    def get_headers(self, token):
        return {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": "My User Agent 1.0",
            "Authorization": "Bearer {}".format(token),
        }

    def update_product_status_magento(self, store_code, sku, status):
        instance = request.env["magento.instance"].sudo().search([], limit=1)
        instance_url = instance.magento_url
        instance_access_token = instance.access_token
        headers = self.get_headers(instance_access_token)
        data = [
            {
                "product": {
                    "sku": sku,
                    "status": status,
                }
            }
        ]
        log_book = self.env["common.log.book.ept"].search([("is_data_import_log_book", "=", True)], limit=1)
        if not log_book:
            log_book = self.env["common.log.book.ept"].create({"is_data_import_log_book": True})
        api_url = f"{instance_url}/rest/{store_code}/async/bulk/V1/products/"
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

    def import_xls(self):
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.excel_file))
        product_sku_rno = 1
        for sheet in wb.sheets():
            for row in range(1, sheet.nrows):
                barcode = str(sheet.cell(row, product_sku_rno).value).split(".")[0]
                if self.product_type == "configurable":
                    product_id = self.env["magento.product.configurable"].search([("magento_sku", "=", barcode)])
                if self.product_type == "simple":
                    product_id = self.env["product.template"].search([("default_code", "=", barcode)])
                    product_id |= self.env["product.template"].search(
                        [("default_code", "=", barcode), ("active", "=", False)]
                    )
                if not product_id:
                    raise UserError(_("Product not found at row %s" % (row + 1)))
                # uk_tiger = sheet.cell(row, uk_tiger_rno).value
                # if uk_tiger == 0:
                #     product_id.write(
                #         {
                #             "uk_tiger_one_boolean": False,
                #         }
                #     )
                #     self.update_product_status_magento("tigerone_uk_store_view", product_id.default_code, 2)
                # elif uk_tiger == 1:
                #     product_id.write(
                #         {
                #             "uk_tiger_one_boolean": True,
                #         }
                #     )
                #     self.update_product_status_magento("tigerone_uk_store_view", product_id.default_code, 1)
                # eu_tiger = sheet.cell(row, eu_tiger_rno).value
                # if eu_tiger == 0:
                #     product_id.write(
                #         {
                #             "eu_tiger_one_boolean": False,
                #         }
                #     )
                #     self.update_product_status_magento("tigerone_eu_store_view", product_id.default_code, 2)
                # elif eu_tiger == 1:
                #     product_id.write(
                #         {
                #             "eu_tiger_one_boolean": True,
                #         }
                #     )
                #     self.update_product_status_magento("tigerone_eu_store_view", product_id.default_code, 1)
                # sa_tiger = sheet.cell(row, sa_tiger_rno).value
                # if sa_tiger == 0:
                #     product_id.write(
                #         {
                #             "sa_tiger_one_boolean": False,
                #         }
                #     )
                #     self.update_product_status_magento("tigerone_sa_store_view", product_id.default_code, 2)
                # elif sa_tiger == 1:
                #     product_id.write(
                #         {
                #             "sa_tiger_one_boolean": True,
                #         }
                #     )
                #     self.update_product_status_magento("tigerone_sa_store_view", product_id.default_code, 1)
                # usa_tiger = sheet.cell(row, usa_tiger_rno).value
                # if usa_tiger == 0:
                #     product_id.write(
                #         {
                #             "usa_tiger_one_boolean": False,
                #         }
                #     )
                #     self.update_product_status_magento("tigerone_us_store_view", product_id.default_code, 2)
                # elif usa_tiger == 1:
                #     product_id.write(
                #         {
                #             "usa_tiger_one_boolean": True,
                #         }
                #     )
                #     self.update_product_status_magento("tigerone_us_store_view", product_id.default_code, 1)
                # uk_seedsman = sheet.cell(row, uk_seedsman_rno).value
                # if uk_seedsman == 0:
                #     product_id.write(
                #         {
                #             "uk_seedsman_boolean": False,
                #         }
                #     )
                #     self.update_product_status_magento("uk", product_id.default_code, 2)
                # elif uk_seedsman == 1:
                #     product_id.write(
                #         {
                #             "uk_seedsman_boolean": True,
                #         }
                #     )
                #     self.update_product_status_magento("uk", product_id.default_code, 1)
                # eu_seedsman = sheet.cell(row, eu_seedsman_rno).value
                # if eu_seedsman == 0:
                #     product_id.write(
                #         {
                #             "eu_seedsman_boolean": False,
                #         }
                #     )
                #     self.update_product_status_magento("eu", product_id.default_code, 2)
                # elif eu_seedsman == 1:
                #     product_id.write(
                #         {
                #             "eu_seedsman_boolean": True,
                #         }
                #     )
                #     self.update_product_status_magento("eu", product_id.default_code, 1)
                # sa_seedsman = sheet.cell(row, sa_seedsman_rno).value
                # if sa_seedsman == 0:
                #     product_id.write(
                #         {
                #             "sa_seedsman_boolean": False,
                #         }
                #     )
                #     self.update_product_status_magento("za", product_id.default_code, 2)
                # elif sa_seedsman == 1:
                #     product_id.write(
                #         {
                #             "sa_seedsman_boolean": True,
                #         }
                #     )
                #     self.update_product_status_magento("za", product_id.default_code, 1)
                # usa_seedsman = sheet.cell(row, usa_seedsman_rno).value
                # if usa_seedsman == 0:
                #     product_id.write(
                #         {
                #             "usa_seedsman_boolean": False,
                #         }
                #     )
                #     self.update_product_status_magento("us", product_id.default_code, 2)
                # elif usa_seedsman == 1:
                #     product_id.write(
                #         {
                #             "usa_seedsman_boolean": True,
                #         }
                #     )
                #     self.update_product_status_magento("us", product_id.default_code, 1)
                # uk_eztestkits = sheet.cell(row, uk_eztestkits_rno).value
                # if uk_eztestkits == 0:
                #     product_id.write(
                #         {
                #             "uk_eztestkits_boolean": False,
                #         }
                #     )
                #     self.update_product_status_magento("eztestkits_uk_store_view", product_id.default_code, 2)
                # elif uk_eztestkits == 1:
                #     product_id.write(
                #         {
                #             "uk_eztestkits_boolean": True,
                #         }
                #     )
                #     self.update_product_status_magento("eztestkits_uk_store_view", product_id.default_code, 1)
                # eu_eztestkits = sheet.cell(row, eu_eztestkits_rno).value
                # if eu_eztestkits == 0:
                #     product_id.write(
                #         {
                #             "eu_eztestkits_boolean": False,
                #         }
                #     )
                #     self.update_product_status_magento("eztestkits_eu_store_view", product_id.default_code, 2)
                # elif eu_eztestkits == 1:
                #     product_id.write(
                #         {
                #             "eu_eztestkits_boolean": True,
                #         }
                #     )
                #     self.update_product_status_magento("eztestkits_eu_store_view", product_id.default_code, 1)
                # sa_eztestkits = sheet.cell(row, sa_eztestkits_rno).value
                # if sa_eztestkits == 0:
                #     product_id.write(
                #         {
                #             "sa_eztestkits_boolean": False,
                #         }
                #     )
                #     self.update_product_status_magento("eztestkits_sa_store_view", product_id.default_code, 2)
                # elif sa_eztestkits == 1:
                #     product_id.write(
                #         {
                #             "sa_eztestkits_boolean": True,
                #         }
                #     )
                #     self.update_product_status_magento("eztestkits_sa_store_view", product_id.default_code, 1)
                # usa_eztestkits = sheet.cell(row, usa_eztestkits_rno).value
                # if usa_eztestkits == 0:
                #     product_id.write(
                #         {
                #             "usa_eztestkits_boolean": False,
                #         }
                #     )
                #     self.update_product_status_magento("eztestkits_usa_store_view", product_id.default_code, 2)
                # elif usa_eztestkits == 1:
                #     product_id.write(
                #         {
                #             "usa_eztestkits_boolean": True,
                #         }
                #     )
                #     self.update_product_status_magento("eztestkits_usa_store_view", product_id.default_code, 1)
                # pytho_nation = sheet.cell(row, pytho_n_rno).value
                # if pytho_nation == 0:
                #     product_id.write(
                #         {
                #             "pytho_n_boolean": False,
                #         }
                #     )
                #     self.update_product_status_magento("pytho_nation_store_view", product_id.default_code, 2)
                # elif pytho_nation == 1:
                #     product_id.write(
                #         {
                #             "pytho_n_boolean": True,
                #         }
                #     )
                #     self.update_product_status_magento("pytho_nation_store_view", product_id.default_code, 1)
                # product_visibility = sheet.cell(row, product_visibility_rno).value
                # if product_visibility:
                #     if product_visibility == 'Not visible individually':
                #         product_visibility_val = '1'
                #     elif  product_visibility == 'Catalog':
                #         product_visibility_val = '2'
                #     elif  product_visibility == 'Search':
                #         product_visibility_val = '3'
                #     elif  product_visibility == 'Catalog,Search':
                #         product_visibility_val = '4'
                #     if product_visibility_val:
                #         product_id.write(
                #             {
                #                 "product_visibility": product_visibility_val,
                #             }
                #         )
                # description = sheet.cell(row, description_rno).value
                # if description:
                #     product_id.write(
                #         {
                #             "description": description,
                #         }
                #     )
                # categ = sheet.cell(row, categ_rno).value
                # categ_id = self.env["product.category"].search(
                #                 [("name", "=", categ)], limit=1
                #             )
                # if categ_id:
                #     product_id.write(
                #         {
                #             "categ_id": categ_id.id,
                #         }
                #     )

                # brand = sheet.cell(row, brand_rno).value
                # brand_id = self.env["product.breeder"].search(
                #                 [("breeder_name", "=", brand)], limit=1
                #             )
                # if brand_id:
                #     if self.product_type == 'configurable':
                #         product_id.write(
                #             {
                #                 "brand_id": brand_id.id,
                #             }
                #         )
                #     else:
                #         product_id.write(
                #         {
                #             "product_breeder_id": brand_id.id,
                #         }
                #     )
                for col in range(1, sheet.ncols):
                    col_val = str(sheet.cell(0, col).value)
                    col_vals = str(sheet.cell(row, col).value)
                    if col_vals:
                        attribute_id = self.env["magento.attribute"].search([("name", "=", col_val)])
                        if attribute_id:
                            product_attribute_id = self.env["product.magento.attribute"].search(
                                [
                                    ("magento_product_config_id", "=", product_id.id),
                                    ("magento_attribute_id", "=", attribute_id.id),
                                ]
                            )
                            if product_attribute_id:
                                product_attribute_id.write({"name": col_vals})
                            else:
                                vals = {
                                    "name": col_vals,
                                    "magento_product_config_id": product_id.id,
                                    "magento_attribute_id": attribute_id.id,
                                }
                                product_attribute_id = self.env["product.magento.attribute"].create(vals)

        return {
            "effect": {
                "fadeout": "slow",
                "message": "Updated!",
                "img_url": "/web/static/src/img/smile.svg",
                "type": "rainbow_man",
            }
        }
