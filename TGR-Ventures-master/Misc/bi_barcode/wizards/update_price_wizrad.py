from odoo import fields, models, _
from odoo.exceptions import UserError
import base64
import xlrd


class UpdateSalePriceWizard(models.TransientModel):
    _name = "update.sale.price.wizard"
    _description = "Update Price Wizard"

    upload = fields.Binary("Upload File", attachment=True)

    def generate_template(self):
        return self.env.ref("bi_barcode.action_export_price_template").report_action(self, config=False)

    def import_prices(self):
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.upload))
        product_id_rno = 0

        retail_default_price_rno = 1
        wholesale_price_rno = 2
        last_cost_rno = 3
        retail_uk_price_rno = 4
        wholesale_uk_rno = 5
        retail_us_price_rno = 6
        wholesale_us_rno = 7
        wholesale_za_rno = 8
        retail_za_rno = 9
        retail_special_us_rno = 10
        retail_special_za_rno = 11
        retail_special_uk_rno = 12
        retail_special_price_rno = 13
        wholesale_special_us_rno = 14
        wholesale_special_price_rno = 15
        wholesale_special_za_rno = 16
        wholesale_special_uk_rno = 17

        imported_sku_count = 0
        for sheet in wb.sheets():
            for row in range(1, sheet.nrows):
                sku = str(sheet.cell(row, product_id_rno).value).split(".")[0]
                product_id = self.env["product.template"].search([("default_code", "=", sku)])
                if not product_id:
                    raise UserError(_(f"Product with SKU {sku} not found in Odoo."))
                retail_price_value = sheet.cell(row, retail_default_price_rno).value
                wholesale_price_value = sheet.cell(row, wholesale_price_rno).value
                last_cost = sheet.cell(row, last_cost_rno).value
                retail_uk_price = sheet.cell(row, retail_uk_price_rno).value
                wholesale_uk_price = sheet.cell(row, wholesale_uk_rno).value
                retail_us_price = sheet.cell(row, retail_us_price_rno).value
                wholesale_us_price = sheet.cell(row, wholesale_us_rno).value
                wholesale_za_price = sheet.cell(row, wholesale_za_rno).value
                retail_za_price = sheet.cell(row, retail_za_rno).value
                retail_special_us = sheet.cell(row, retail_special_us_rno).value
                retail_special_za = sheet.cell(row, retail_special_za_rno).value
                retail_special_uk = sheet.cell(row, retail_special_uk_rno).value
                retail_special_price = sheet.cell(row, retail_special_price_rno).value
                wholesale_special_us = sheet.cell(row, wholesale_special_us_rno).value
                wholesale_special_price = sheet.cell(row, wholesale_special_price_rno).value
                wholesale_special_za = sheet.cell(row, wholesale_special_za_rno).value
                wholesale_special_uk = sheet.cell(row, wholesale_special_uk_rno).value

                if wholesale_price_value != "":
                    product_id.write(
                        {
                            "wholesale_price_value": wholesale_price_value,
                        }
                    )
                if retail_price_value != "":
                    product_id.write(
                        {
                            "retail_default_price": retail_price_value,
                        }
                    )
                if last_cost != "":
                    product_id.write(
                        {
                            "last_cost_2": last_cost,
                        }
                    )
                if retail_uk_price != "":
                    product_id.write(
                        {
                            "retail_uk_price": retail_uk_price,
                        }
                    )
                if wholesale_uk_price != "":
                    product_id.write(
                        {
                            "wholesale_uk": wholesale_uk_price,
                        }
                    )

                if retail_us_price != "":
                    product_id.write(
                        {
                            "retail_us_price": retail_us_price,
                        }
                    )
                if wholesale_us_price != "":
                    product_id.write(
                        {
                            "wholesale_us": wholesale_us_price,
                        }
                    )

                if wholesale_za_price != "":
                    product_id.write(
                        {
                            "wholesale_za": wholesale_za_price,
                        }
                    )
                if retail_za_price != "":
                    product_id.write(
                        {
                            "retail_za_price": retail_za_price,
                        }
                    )
                if retail_special_price != "":
                    product_id.write(
                        {
                            "retail_special_price": retail_special_price,
                        }
                    )

                if retail_special_us != "":
                    product_id.write(
                        {
                            "retail_special_us": retail_special_us,
                        }
                    )
                if retail_special_za != "":
                    product_id.write(
                        {
                            "retail_special_za": retail_special_za,
                        }
                    )
                if retail_special_uk != "":
                    product_id.write(
                        {
                            "retail_special_uk": retail_special_uk,
                        }
                    )
                if wholesale_special_price != "":
                    product_id.write(
                        {
                            "wholesale_special_price": wholesale_special_price,
                        }
                    )
                if wholesale_special_us != "":
                    product_id.write(
                        {
                            "wholesale_special_us": wholesale_special_us,
                        }
                    )
                if wholesale_special_uk != "":
                    product_id.write(
                        {
                            "wholesale_special_uk": wholesale_special_uk,
                        }
                    )
                if wholesale_special_za != "":
                    product_id.write(
                        {
                            "wholesale_special_za": wholesale_special_za,
                        }
                    )

                imported_sku_count += 1
        return {
            "effect": {
                "fadeout": "slow",
                "message": f"{imported_sku_count} records successfully imported",
                "img_url": "/web/static/img/smile.svg",
                "type": "rainbow_man",
            }
        }
