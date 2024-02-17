from odoo import _, fields, models, api
from odoo.exceptions import UserError
import xlrd
import base64


class ImportLineData(models.Model):
    _inherit = "sale.order"

    excel_file = fields.Binary(string="Excel File", attachment=True)
    vendor_line_id = fields.Many2one("res.partner", string="Vendor")

    @api.onchange("vendor_line_id")
    def _onchange_vendor_line_id(self):
        for each in self.order_line:
            if each.product_id:
                each.vendor_id = self.vendor_line_id

    def export_template(self):
        return self.env.ref("bi_sale_line_import.action_line_export_template").report_action(self, config=False)

    def load_lines(self):
        for record in self:
            if record.excel_file:
                values = []
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(record.excel_file))
                count = 0
                for sheet in workbook.sheets():
                    product_col = 0
                    line_qty = 1
                    unit_price = 2
                    tax = 3
                    discount_percent = 4
                    for row in range(1, sheet.nrows):
                        try:
                            product_id = self.env["product.product"].search(
                                [("default_code", "=", sheet.cell(row, product_col).value)], limit=1
                            )
                            if not product_id:
                                raise UserError(_("Product not found at row %s" % (row + 1)))

                            product_qty = sheet.cell(row, line_qty).value or 1
                            if product_qty <= 0:
                                raise UserError(_("Quantity should be greater than zero at row %s" % (row + 1)))
                            product_price = sheet.cell(row, unit_price).value
                            if not product_price:
                                if self.env.user.company_id.id == 10:
                                    product_price = product_id.wholesale_price_value
                                elif self.env.user.company_id.id == 11:
                                    product_price = product_id.wholesale_us
                            # if not product_price:
                            # raise UserError(_("Price should be greater than zero at row %s" % (row + 1)))
                            discount = sheet.cell(row, discount_percent).value
                            if not bool(discount) or float(discount) < 0:
                                discount = 0
                            tax_name = sheet.cell(row, tax).value
                            taxes = []
                            if bool(tax_name):
                                tax_id = self.env["account.tax"].search([("name", "=", tax_name)], limit=1)
                                # if not tax_id:
                                #     raise UserError(_("Tax at row %s not found" % (row + 1)))
                                # else:
                                #     taxes.append((4, tax_id.id))
                            if not self.pricelist_id:
                                values.append(
                                    (
                                        0,
                                        0,
                                        {
                                            "product_id": product_id.id,
                                            "name": product_id.name,
                                            "product_uom": product_id.uom_id.id,
                                            "product_uom_qty": product_qty,
                                            "price_unit": product_price if product_price else 0,
                                            "tax_id": taxes,
                                            "discount": discount,
                                        },
                                    )
                                )
                            if self.pricelist_id:
                                if product_id.product_tmpl_id.id in self.pricelist_id.item_ids.product_tmpl_id.ids:
                                    for line in self.pricelist_id.item_ids:
                                        if line.product_tmpl_id.id == product_id.product_tmpl_id.id:
                                            values.append(
                                                (
                                                    0,
                                                    0,
                                                    {
                                                        "product_id": product_id.id,
                                                        "name": product_id.name,
                                                        "product_uom": product_id.uom_id.id,
                                                        "product_uom_qty": product_qty,
                                                        "price_unit": line.fixed_price,
                                                        "tax_id": taxes,
                                                        "discount": discount,
                                                    },
                                                )
                                            )
                                else:
                                    values.append(
                                        (
                                            0,
                                            0,
                                            {
                                                "product_id": product_id.id,
                                                "name": product_id.name,
                                                "product_uom": product_id.uom_id.id,
                                                "product_uom_qty": product_qty,
                                                "price_unit": product_price if product_price else 0,
                                                "tax_id": taxes,
                                                "discount": discount,
                                            },
                                        )
                                    )
                            count += 1
                        except IndexError:
                            break
                        row += 1
                    values = {
                        "order_line": values,
                    }
                    self.write(values)
                    self.excel_file = False
            else:
                raise UserError(_("Please Select Excel File"))
        return {
            "effect": {
                "fadeout": "slow",
                "message": f"{count } records successfully imported",
                "img_url": "/web/static/img/smile.svg",
                "type": "rainbow_man",
            }
        }
