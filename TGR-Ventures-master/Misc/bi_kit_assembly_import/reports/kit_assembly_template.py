from odoo import models


class KitAssemblyTemplate(models.AbstractModel):
    _name = "report.bi_kit_assembly_import.kit_assembly_template"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet("Kit Assembly Import Data")
        sheet.set_column("A:A", 20)
        sheet.set_column("B:B", 25)
        sheet.set_column("C:C", 12)
        sheet.set_column("D:D", 25)
        sheet.set_column("E:E", 12)
        sheet.set_row(0, 30)
        # sheet.set_column('F:F', 20)
        # sheet.set_column('G:G', 20)
        # sheet.set_column('H:H', 20)
        # sheet.set_column('I:I', 20)
        # sheet.set_column('J:J', 20)
        # sheet.set_column('K:K', 20)
        # sheet.set_column('L:L', 20)
        # sheet.set_column('M:M', 20)
        # sheet.set_column('N:N', 20)
        # sheet.set_column('O:O', 20)
        # sheet.write('A1','Product SKU')
        # sheet.write('B1','Quantity')
        # sheet.write('C1','Warehouse')
        # sheet.write('D1','Kit Product 1 SKU')
        # sheet.write('E1','Quantity')
        # sheet.write('F1','Kit Product 2 SKU')
        # sheet.write('G1','Quantity')
        # sheet.write('H1','Kit Product 3 SKU')
        # sheet.write('I1','Quantity')
        # sheet.write('J1','Kit Product 4 SKU')
        # sheet.write('K1','Quantity')
        # sheet.write('L1','Kit Product 5 SKU')
        # sheet.write('M1','Quantity')
        # sheet.write('N1','Kit Product 6 SKU')
        # sheet.write('O1','Quantity')

        table_head_format = workbook.add_format(
            {"align": "center", "border": 1, "valign": "vcenter", "bg_color": "#D6D6D6"}
        )

        sheet.write("A1", "Warehouse", table_head_format)
        sheet.write("B1", "Source SKU", table_head_format)
        sheet.write("C1", "Source \nSKU Qty", table_head_format)
        sheet.write("D1", "Destination SKU", table_head_format)
        sheet.write("E1", "Destination \nSKU Qty", table_head_format)
