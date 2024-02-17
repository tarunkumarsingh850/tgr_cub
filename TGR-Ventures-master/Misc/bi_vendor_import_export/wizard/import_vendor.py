import base64
import xlrd
from odoo.exceptions import UserError
from odoo import fields, models, _


class BiImportVendor(models.TransientModel):
    _name = "import.vendor"
    _description = "Import Vendor"

    excel_file = fields.Binary("Upload Excel", attachment=True, required=True)

    def import_xls(self):
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.excel_file))
        values = {}
        excel_heading = []
        count = 0
        sl_col = 0

        for sheet in wb.sheets():
            for i in range(0, sheet.nrows):
                for j in range(0, sheet.ncols):
                    if i == 0:
                        heading = sheet.cell(i, j).value
                        if heading in [
                            "Vendor ID",
                            "Name",
                            "Street",
                            "Street2",
                            "City",
                            "State",
                            "Country",
                            "Zip",
                            "Vat",
                            "Vendor Class",
                            "Phone",
                            "Mobile",
                            "Email",
                            "Website",
                            "Payment Terms",
                            "Lead Days",
                            "Delivery Method",
                            "Taxes",
                            "Acumatica Status",
                            "Attention",
                            "Vendor External ID",
                            "Curr. Rate Type",
                            "Payment Method",
                            "Payment By",
                            "Warehouse",
                            "Delivery Estimate",
                            "Discount - Comments",
                            "Ordering Method",
                            "Password",
                            "Username",
                            "Tax Zone",
                        ]:
                            excel_heading.append(heading)
                        else:
                            raise UserError(_("Incorrect Excel format %s") % heading)
                    else:
                        vat = 0
                        vat = 0
                        phone = 0
                        phone_2 = 0
                        zip_n = 0
                        if sheet.cell(i, sl_col).value:
                            if excel_heading[j] == "Vendor ID":
                                vendor_id = sheet.cell(i, j).value
                                if type(vendor_id) == str:
                                    values["name"] = str(vendor_id)
                            elif excel_heading[j] == "Name":
                                values["vendor_code"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Street":
                                values["street"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Street2":
                                values["street2"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "City":
                                values["city"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Country":
                                country = sheet.cell(i, j).value
                                country_id = self.env["res.country"].search([("name", "=", country)], limit=1)
                                if not country_id:
                                    country_id = self.env["res.country"].search(
                                        [("name", "=", country.capitalize())], limit=1
                                    )
                                if country_id:
                                    values["country_id"] = country_id.id
                                else:
                                    if country:
                                        raise UserError(_("'%s' not a valid country") % (country))
                            elif excel_heading[j] == "State":
                                state_name = sheet.cell(i, j).value
                                state = self.env["res.country.state"].search([("name", "=", state_name)], limit=1)
                                if not state:
                                    state = self.env["res.country.state"].search(
                                        [("name", "=", state_name.capitalize())], limit=1
                                    )
                                if state:
                                    values["state_id"] = state.id
                                else:
                                    if state:
                                        raise UserError(_("'%s' not a valid state") % (state))
                            elif excel_heading[j] == "Zip":
                                zip_n = sheet.cell(i, j).value
                                if type(zip_n) == float:
                                    zip_n = int(zip_n)
                                values["zip"] = str(zip_n)
                            elif excel_heading[j] == "Vat":
                                vat = sheet.cell(i, j).value
                                if type(vat) == float:
                                    vat = int(vat)
                                values["vat"] = str(vat)
                            elif excel_heading[j] == "Vendor Class":
                                vendor_class = sheet.cell(i, j).value
                                class_vendor = self.env["vendor.class"].search([("name", "=", vendor_class)], limit=1)
                                if not class_vendor:
                                    class_vendor = self.env["vendor.class"].search(
                                        [("name", "=", vendor_class.capitalize())], limit=1
                                    )
                                if class_vendor:
                                    values["vendor_class_id"] = class_vendor.id
                                else:
                                    if state:
                                        raise UserError(_("'%s' not a valid Vendor Class") % (vendor_class))
                            elif excel_heading[j] == "Phone 1":
                                phone = sheet.cell(i, j).value
                                if type(phone) == float:
                                    phone = int(phone)
                                values["phone"] = str(phone)
                            elif excel_heading[j] == "Mobile":
                                phone_2 = sheet.cell(i, j).value
                                if type(phone_2) == float:
                                    phone_2 = int(phone_2)
                                values["mobile"] = str(phone_2)
                            elif excel_heading[j] == "Email":
                                values["email"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Website":
                                values["website"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Payment Terms":
                                payment_terms = sheet.cell(i, j).value
                                payment_terms_id = self.env["account.payment.term"].search(
                                    [("name", "=", payment_terms)], limit=1
                                )
                                if payment_terms:
                                    if payment_terms_id:
                                        values["property_supplier_payment_term_id"] = payment_terms_id.id
                                    else:
                                        raise UserError(_("'%s' not a Payment Term") % (payment_terms))
                            elif excel_heading[j] == "Lead Days":
                                values["lead_days"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Delivery Method":
                                delivery_method = sheet.cell(i, j).value
                                delivery_method_id = self.env["delivery.carrier"].search(
                                    [("name", "=", delivery_method)], limit=1
                                )
                                if delivery_method:
                                    if delivery_method_id:
                                        values["property_delivery_carrier_id"] = delivery_method_id.id
                                    else:
                                        raise UserError(_("'%s' not a Delivery Method") % (delivery_method))
                            elif excel_heading[j] == "Taxes":
                                taxes = sheet.cell(i, j).value
                                tax = str(taxes).split(",")
                                for t in tax:
                                    account_tax_id = self.env["account.tax"].search([("code", "=", t)], limit=1)
                                    if t:
                                        if account_tax_id:
                                            values["taxes_ids"] = [(4, account_tax_id.id)]
                                        else:
                                            raise UserError(_("'%s' not a Tax") % (t))
                            elif excel_heading[j] == "Acumatica Status":
                                values["vendor_status"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Attention":
                                values["vendor_attention"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Vendor External ID":
                                values["vendor_external_id"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Curr. Rate Type":
                                values["vendor_rate_type"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Payment Method":
                                values["vendor_payment_method"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Payment By":
                                values["vendor_payment_by"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Warehouse":
                                values["vendor_warehouse"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Delivery Estimate":
                                values["vendor_delivery_estimate"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Discount - Comments":
                                values["vendor_discount_comment"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Ordering Method":
                                values["vendor_ordering_method"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Password":
                                values["vendor_password"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Username":
                                values["vendor_username"] = sheet.cell(i, j).value
                            elif excel_heading[j] == "Tax Zone":
                                values["tax_zone"] = sheet.cell(i, j).value

                if values:
                    values["is_supplier"] = True
                    vendor = self.env["res.partner"].search([("is_supplier", "=", True), ("name", "=", values["name"])])
                    if vendor:
                        vendor.update(values)
                    else:
                        self.env["res.partner"].sudo().create(values)
                    count += 1
                    values = {}

        return {
            "effect": {
                "fadeout": "slow",
                "message": " {} Vendors Imported!".format(str(count)),
                "img_url": "/web/static/src/img/smile.svg",
                "type": "rainbow_man",
            }
        }
