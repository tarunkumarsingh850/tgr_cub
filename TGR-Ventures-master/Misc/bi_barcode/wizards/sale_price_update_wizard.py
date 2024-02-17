from odoo import fields, models, _
from odoo.exceptions import UserError
import base64
import xlrd
import os
from datetime import datetime


class SalePriceUpdateWizard(models.TransientModel):
    _name = "sale.price.update.wizard"
    _description = "Sale Price Update Wizard"

    filename = fields.Char(string="File name")
    csv_file = fields.Binary("Upload File", attachment=True)
    # line_ids = fields.One2many('sale.price.lines', 'top_id', string='Products')

    def generate_template(self):
        return self.env.ref("bi_barcode.action_export_template").report_action(self, config=False)

    def generate_update(self):
        if self.csv_file:
            file_value = self.csv_file.decode("utf-8")
            filename, FileExtension = os.path.splitext(self.filename)
            if FileExtension == ".csv":
                input_file = base64.b64decode(file_value)
                lst = []
                for loop in input_file.decode("utf-8"):
                    lst.append(loop)
                lsts = input_file.decode("utf-8").split("\n")
                lsts.pop(0)
                # print (sdf)
                for rec in lsts:
                    if rec:
                        code = rec.split(",")
                        product_id = self.env["product.template"].search([("default_code", "=", code[0])])
                        product_id.write(
                            {
                                "lst_price": code[1],
                                "standard_price": code[2],
                                "min_cost": code[3],
                                "max_cost": code[4],
                                "retail_uk_price": code[5],
                                "retail_us_price": code[6],
                                "retail_default_price": code[7],
                                "retail_special_price": code[8],
                                "wholesale_special_price": code[9],
                                "case_quantity": code[10],
                            }
                        )
            else:
                wb = xlrd.open_workbook(file_contents=base64.decodestring(self.csv_file))
                product_id_rno = 0
                barcode_rno = 1
                case_quantity_rno = 2
                out_of_stock_rno = 3
                pending_discountinue_rno = 4
                exclude_replenish_rno = 5
                exclude_pricelist_rno = 6
                exclude_customer_rno = 7
                back_stock_date_rno = 8
                supplier_sku_rno = 9
                is_pn_us_two_rno = 10
                is_pn_us_rno = 11
                is_pn_br_rno = 12
                is_pn_sa_rno = 13
                out_of_stock_date_rno = 14

                product_tag_rno = 15
                remove_product_tag_rno = 16
                weight_rno = 17
                usa_replenishment_rno = 18
                malaga_relenishment_rno = 19
                uk_replenishment_rno = 20
                hs_code_rno = 21
                free_product_rno = 22
                out_stock = None
                count = 0
                error_list = []
                for sheet in wb.sheets():
                    for row in range(1, sheet.nrows):
                        sku = str(sheet.cell(row, product_id_rno).value).split(".")[0]
                        product_id = self.env["product.template"].search([("default_code", "=", sku)])
                        if product_id:
                            barcode_value = sheet.cell(row, barcode_rno).value

                            case_quantity = sheet.cell(row, case_quantity_rno).value
                            out_of_stock = sheet.cell(row, out_of_stock_rno).value
                            back_stock_date = sheet.cell(row, back_stock_date_rno).value
                            supplier_sku_no = sheet.cell(row, supplier_sku_rno).value
                            out_of_stock_date = sheet.cell(row, out_of_stock_date_rno).value
                            product_tags = sheet.cell(row, product_tag_rno).value
                            remove_product_tags = sheet.cell(row, remove_product_tag_rno).value
                            weight = sheet.cell(row, weight_rno).value
                            usa_replenishment = sheet.cell(row, usa_replenishment_rno).value
                            malaga_relenishment = sheet.cell(row, malaga_relenishment_rno).value
                            uk_replenishment = sheet.cell(row, uk_replenishment_rno).value
                            hs_code = sheet.cell(row, hs_code_rno).value
                            free_product = sheet.cell(row, free_product_rno).value

                            if barcode_value:
                                if isinstance(barcode_value, float) or isinstance(barcode_value, int):
                                    barcode_value = str(int(barcode_value))
                                else:
                                    barcode_value = str(barcode_rno)

                                product_id.barcode = barcode_value

                            if out_of_stock == 1:
                                out_stock = True
                            if out_of_stock == 0:
                                out_stock = False
                            if out_of_stock == 1 or out_of_stock == 0:
                                product_id.write(
                                    {
                                        "is_out_of_stock": out_stock,
                                    }
                                )
                            elif out_of_stock != "":
                                error_list.append("Out of Stock not updated for {}".format(product_id.name))

                            pending_discontinue = sheet.cell(row, pending_discountinue_rno).value
                            if pending_discontinue == 0 or pending_discontinue == 1:
                                if pending_discontinue == 1:
                                    pending_discontinue_value = True
                                if pending_discontinue == 0:
                                    pending_discontinue_value = False
                                product_id.write(
                                    {
                                        "is_pending_discontinued": pending_discontinue_value,
                                    }
                                )
                            elif pending_discontinue != "":
                                error_list.append("Pending Discontinued not updated for {}".format(product_id.name))

                            exclude_replenish = sheet.cell(row, exclude_replenish_rno).value
                            if exclude_replenish == 0 or exclude_replenish == 1:
                                if exclude_replenish == 1:
                                    exclude_replenish_value = True
                                if exclude_replenish == 0:
                                    exclude_replenish_value = False
                                product_id.write(
                                    {
                                        "is_exclude_from_replenishment": exclude_replenish_value,
                                    }
                                )
                            elif exclude_replenish != "":
                                error_list.append(
                                    "Exclude from Replenishment not updated for {}".format(product_id.name)
                                )

                            exclude_pricelist = sheet.cell(row, exclude_pricelist_rno).value
                            if exclude_pricelist == 0 or exclude_pricelist == 1:
                                if exclude_pricelist == 1:
                                    exclude_pricelist_value = True
                                if exclude_pricelist == 0:
                                    exclude_pricelist_value = False

                                product_id.write(
                                    {
                                        "is_excluded_pricelist": exclude_pricelist_value,
                                    }
                                )
                            elif exclude_pricelist != "":
                                error_list.append("Exclude from Pricelist not updated for {}".format(product_id.name))

                            exclude_customer = sheet.cell(row, exclude_customer_rno).value
                            if exclude_customer == 0 or exclude_customer == 1:
                                if exclude_customer == 1:
                                    exclude_customer_value = True
                                if exclude_customer == 0:
                                    exclude_customer_value = False

                                product_id.write(
                                    {
                                        "is_excluded_customer": exclude_customer_value,
                                    }
                                )
                            elif exclude_customer != "":
                                error_list.append("Exclude from customers not updated for {}".format(product_id.name))

                            if back_stock_date != "":
                                seconds = (back_stock_date - 25569) * 86400.0
                                back_stock_date = datetime.utcfromtimestamp(seconds)
                                product_id.write(
                                    {
                                        "back_stock_date": back_stock_date,
                                        "is_back_in_stock": True,
                                    }
                                )
                            if supplier_sku_no != "":
                                if isinstance(supplier_sku_no, float):
                                    supplier_sku_no = int(supplier_sku_no)
                                product_id.write(
                                    {
                                        "supplier_sku_no": str(supplier_sku_no),
                                    }
                                )

                            is_pn_us_two = sheet.cell(row, is_pn_us_two_rno).value
                            if is_pn_us_two == 1 or is_pn_us_two == 0:
                                if is_pn_us_two == 1:
                                    is_pn_us_two_value = True
                                if is_pn_us_two == 0:
                                    is_pn_us_two_value = False
                                product_id.write(
                                    {
                                        "is_pn_us_two": is_pn_us_two_value,
                                    }
                                )
                            elif is_pn_us_two != "":
                                error_list.append("T1 US not updated for {}".format(product_id.name))

                            is_pn_us = sheet.cell(row, is_pn_us_rno).value
                            if is_pn_us == 0 or is_pn_us == 1:
                                if is_pn_us == 1:
                                    is_pn_us_value = True
                                if is_pn_us == 0:
                                    is_pn_us_value = False

                                product_id.write(
                                    {
                                        "is_pn_us": is_pn_us_value,
                                    }
                                )
                            elif is_pn_us != "":
                                error_list.append("Phytonation not updated for {}".format(product_id.name))

                            is_pn_br = sheet.cell(row, is_pn_br_rno).value
                            if is_pn_br == 0 or is_pn_br == 1:
                                if is_pn_br == 1:
                                    is_pn_br_value = True
                                if is_pn_br == 0:
                                    is_pn_br_value = False

                                product_id.write(
                                    {
                                        "is_pn_br": is_pn_br_value,
                                    }
                                )
                            elif is_pn_br != "":
                                error_list.append("PN BR not updated for {}".format(product_id.name))

                            is_pn_sa = sheet.cell(row, is_pn_sa_rno).value
                            if is_pn_sa == 0 or is_pn_sa == 1:
                                if is_pn_sa == 1:
                                    is_pn_sa_value = True
                                if is_pn_sa == 0:
                                    is_pn_sa_value = False

                                product_id.write(
                                    {
                                        "is_pn_sa": is_pn_sa_value,
                                    }
                                )
                            elif is_pn_sa != "":
                                error_list.append("PN SA not updated for {}".format(product_id.name))

                            if case_quantity != "":
                                product_id.write(
                                    {
                                        "case_quantity": case_quantity,
                                    }
                                )

                            if out_of_stock_date != "":
                                seconds = (out_of_stock_date - 25569) * 86400.0
                                out_of_stock_date = datetime.utcfromtimestamp(seconds)
                                product_id.write(
                                    {
                                        "is_out_of_stock": True,
                                        "out_of_stock_date": out_of_stock_date,
                                    }
                                )

                            if product_tags:
                                product_tag_ids = []
                                for tag in product_tags.split(","):
                                    tag_record = self.env["product.tag"].search([("name", "=", tag)])
                                    if not tag_record:
                                        raise UserError(_(f"Tag {tag} does not exist."))
                                    product_tag_ids.append(tag_record.id)
                                for tag_id in product_tag_ids:
                                    product_id.product_tag_ids = [(4, tag_id)]
                            if weight != "":
                                product_id.write(
                                    {
                                        "weight": weight,
                                    }
                                )

                            if usa_replenishment == 0 or usa_replenishment == 1:
                                if usa_replenishment == 1:
                                    usa_replenishment = True
                                if usa_replenishment == 0:
                                    usa_replenishment = False
                                product_id.write({"is_usa_replenishment": usa_replenishment})
                            elif usa_replenishment != "":
                                error_list.append("USA Replenishment Enable not updated for {}".format(product_id.name))

                            if malaga_relenishment == 0 or malaga_relenishment == 1:
                                if malaga_relenishment == 1:
                                    malaga_relenishment = True
                                if malaga_relenishment == 0:
                                    malaga_relenishment = False
                                product_id.write({"is_malaga_replenishment": malaga_relenishment})
                            elif malaga_relenishment != "":
                                error_list.append(
                                    "Malaga Replenishment Enable not updated for {}".format(product_id.name)
                                )

                            if uk_replenishment == 0 or uk_replenishment == 1:
                                if uk_replenishment == 1:
                                    uk_replenishment = True
                                if uk_replenishment == 0:
                                    uk_replenishment = False
                                product_id.write({"is_uk_replenishment": uk_replenishment})
                            elif uk_replenishment != "":
                                error_list.append("UK Replenishment Enable not updated for {}".format(product_id.name))

                            if hs_code:
                                product_id.write({"hs_code": int(hs_code)})

                            if free_product == 0 or free_product == 1:
                                if free_product == 1:
                                    free_product = True
                                if free_product == 0:
                                    free_product = False
                                product_id.write({"is_free_product": free_product})
                            elif free_product != "":
                                error_list.append("Free Products not updated for {}".format(product_id.name))

                            if remove_product_tags:
                                remove_product_tag_ids = []
                                for tag in remove_product_tags.split(","):
                                    tag_record = self.env["product.tag"].search([("name", "=", tag)])
                                    if not tag_record:
                                        raise UserError(_(f"Tag {tag} does not exist."))
                                    remove_product_tag_ids.append(tag_record.id)
                                for remove_tag in remove_product_tag_ids:
                                    product_id.product_tag_ids = [(3, remove_tag)]
                            count += 1
                        else:
                            error_list.append(
                                "Product {} not found. All updation for this product not done.".format(sku)
                            )

        note = ""
        for index, error in enumerate(error_list, start=1):
            note += f"{index}. {error}\n"
        note = note + "\nAll other datas updated."

        if error_list:
            return {
                "name": _("Updation Status"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "updation.status",
                "target": "new",
                "context": {
                    "default_message": note if note != "" else "No Errors in Updation",
                },
            }
        else:
            return {
                "effect": {
                    "fadeout": "slow",
                    "message": f"{count} records successfully imported",
                    "img_url": "/web/static/img/smile.svg",
                    "type": "rainbow_man",
                },
            }
