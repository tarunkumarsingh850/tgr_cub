from odoo import fields, models, _
import base64
import xlrd
from odoo.exceptions import UserError


class MagentoAttributeUpdate(models.TransientModel):
    _name = "magento.attribute.update"
    _description = "Magento Attribute Update"

    upload = fields.Binary("Upload File", attachment=True)

    def generate_template(self):
        return self.env.ref("bi_magento_attribute_import.action_export_template").report_action(self, config=False)

    def generate_update(self):
        if self.upload:
            wb = xlrd.open_workbook(file_contents=base64.decodestring(self.upload))
            product_id_rno = 0
            for sheet in wb.sheets():
                for row in range(1, sheet.nrows):
                    sku = str(sheet.cell(row, product_id_rno).value).split(".")[0]
                    product_id = self.env["product.template"].search([("default_code", "=", sku)])
                    if not product_id:
                        raise UserError(_("Product not found at row %s" % (row + 1)))
                    for col in range(1, sheet.ncols):
                        col_val = str(sheet.cell(0, col).value)
                        col_vals = str(sheet.cell(row, col).value)
                        if col_vals:
                            attribute_id = self.env["magento.attribute"].search([("name", "=", col_val)])
                            if attribute_id:
                                product_attribute_id = self.env["product.magento.attribute"].search(
                                    [("product_id", "=", product_id.id), ("magento_attribute_id", "=", attribute_id.id)]
                                )
                                if product_attribute_id:
                                    product_attribute_id.write({"name": col_vals})
                                else:
                                    vals = {
                                        "name": col_vals,
                                        "product_id": product_id.id,
                                        "magento_attribute_id": attribute_id.id,
                                    }
                                    product_attribute_id = self.env["product.magento.attribute"].create(vals)
