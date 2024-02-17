from odoo import fields, models, _
import binascii
import tempfile
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

try:
    import xlrd
except ImportError:
    _logger.debug("Cannot `import xlrd`.")
try:
    pass
except ImportError:
    _logger.debug("Cannot `import csv`.")
try:
    pass
except ImportError:
    _logger.debug("Cannot `import base64`.")


class MaterialTransferImport(models.Model):
    _name = "material.transfer.import"
    _description = "Material Transfer Import"

    filename = fields.Char(string="File name")
    file = fields.Binary(string="Select File")
    product_details_option = fields.Selection([("from_xls", "Take Details From The XLS File")], default="from_xls")

    def generate_update(self):
        if self.file:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            for row_no in range(sheet.nrows):
                if row_no <= 0:
                    map(lambda row: row.value.encode("utf-8"), sheet.row(row_no))
                else:
                    line = list(
                        map(
                            lambda row: isinstance(row.value, bytes) and row.value.encode("utf-8") or str(row.value),
                            sheet.row(row_no),
                        )
                    )
                    if self.product_details_option == "from_xls":
                        values.update(
                            {
                                "row_no": row_no,
                                "barcode": line[0].split(".")[0],
                                "quantity": line[1],
                            }
                        )
                        self.create_order_line(values)

    def find_line(self, barcode, line):
        product_obj = self.env["product.product"]
        product_search = product_obj.search([("barcode", "=", barcode)])
        if product_search:
            return product_search[0]
        else:
            raise ValidationError(_("The Barcode {} is invalid at line {}".format(barcode, line)))

    def create_order_line(self, values):
        material_request_brw = self.env["material.request"].browse(self._context.get("active_id"))
        barcode = values.get("barcode")
        product_id = self.env["product.product"].search([("barcode", "=", barcode)])
        row_no = values.get("row_no")
        barcode = self.find_line(values.get("barcode"), line=row_no)
        self.env["material.request.line"].create(
            {
                "material_id": material_request_brw.id,
                "product_id": product_id.id,
                "quantity": values.get("quantity"),
                "unit_of_measure": product_id.uom_id.id,
            }
        )
