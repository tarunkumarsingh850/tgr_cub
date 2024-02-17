from odoo import _, fields, models
from odoo.exceptions import UserError
import xlrd
import base64


class KitAssemblyImport(models.TransientModel):
    _name = "kit.assembly.import"
    _description = "Kit Assembly Import"

    file = fields.Binary("File")
    type = fields.Selection([("assembly", "Assembly"), ("dissembly", "Dissembly")], string="Type", default="assembly")

    def export_template(self):
        return self.env.ref("bi_kit_assembly_import.kit_import_template_action").report_action(self, config=False)

    def import_kit_data(self):
        if not self.file:
            raise UserError(_("Select a file to import."))
        workbook = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
        for sheet in workbook.sheets():
            # sku_rno = 0
            # qty_rno = 1
            # warehouse_rno = 2
            # for row in range(1, sheet.nrows):
            #     product = self.env['product.product'].search([('default_code','=',sheet.cell(row, sku_rno).value)])
            #     if not product:
            #         raise UserError(_(f"Product with SKU {sheet.cell(row, sku_rno).value} not found."))
            #     qty = float(sheet.cell(row, qty_rno).value)
            #     warehouse = self.env['stock.warehouse'].search([('name','=',sheet.cell(row, warehouse_rno).value)])
            #     if not product:
            #         raise UserError(_(f"Product with SKU {sheet.cell(row, sku_rno).value} not found."))
            #     assembly_values = {
            #         "product_id": product.id,
            #         "quantity": qty,
            #         "warehouse_id": warehouse.id,
            #         "is_disassembly": True if (self.type == "dissembly") else False
            #     }
            #     assembly_lines = []
            #     for col in range(3, sheet.ncols, 2):
            #         if sheet.cell(row, col).value != '':
            #             line_product = self.env['product.product'].search([('default_code','=',sheet.cell(row, col).value)])
            #             if not line_product:
            #                 raise UserError(f"Product with SKU {sheet.cell(row, col).value} not found.")
            #             else:
            #                 assembly_lines.append((0,0,{
            #                     "product_id": line_product.id,
            #                     "line_uom_id": line_product.uom_id.id,
            #                     "line_quantity": float(sheet.cell(row, col+1).value),
            #                 }))
            #     assembly_values.update({
            #         "kit_line_ids": assembly_lines
            #     })
            #     assembly_id = self.env['kit.assembly'].create(assembly_values)
            #     assembly_id._onchange_product_id_uom()
            #     assembly_id._onchange_warehouse_id()

            warehouse_rno = 0
            source_sku_rno = 1
            source_qty_rno = 2
            desination_sku_rno = 3
            destination_qty_rno = 4

            for row in range(1, sheet.nrows):
                if sheet.cell(row, source_sku_rno).value == "":
                    row += 1
                    continue
                product = self.env["product.product"].search(
                    [("default_code", "=", sheet.cell(row, source_sku_rno).value)]
                )
                if not product:
                    raise UserError(_(f"Product with SKU {sheet.cell(row, source_sku_rno).value} not found."))
                qty = float(sheet.cell(row, source_qty_rno).value)
                warehouse = self.env["stock.warehouse"].search([("name", "=", sheet.cell(row, warehouse_rno).value)])
                if not warehouse and not "":
                    raise UserError(_(f"Warehouse with name {sheet.cell(row, warehouse_rno).value} not found."))
                assembly_values = {
                    "product_id": product.id,
                    "quantity": qty,
                    "warehouse_id": warehouse.id,
                    "is_disassembly": True if (self.type == "dissembly") else False,
                }
                assembly_lines = []

                for row in range(row, sheet.nrows):
                    product_row = row + 1 if row != sheet.nrows - 1 else sheet.nrows - 1
                    if sheet.cell(product_row, source_sku_rno).value == "":
                        if sheet.cell(row, desination_sku_rno).value != "":
                            line_product = self.env["product.product"].search(
                                [("default_code", "=", sheet.cell(row, desination_sku_rno).value)]
                            )
                            if not line_product:
                                raise UserError(
                                    f"Product with SKU {sheet.cell(row, desination_sku_rno).value} not found."
                                )
                            assembly_lines.append(
                                (
                                    0,
                                    0,
                                    {
                                        "product_id": line_product.id,
                                        "line_uom_id": line_product.uom_id.id,
                                        "line_quantity": float(sheet.cell(row, destination_qty_rno).value),
                                    },
                                )
                            )
                    else:
                        if sheet.cell(row, desination_sku_rno).value != "":
                            line_product = self.env["product.product"].search(
                                [("default_code", "=", sheet.cell(row, desination_sku_rno).value)]
                            )
                            if not line_product:
                                raise UserError(
                                    f"Product with SKU {sheet.cell(row, desination_sku_rno).value} not found."
                                )
                            assembly_lines.append(
                                (
                                    0,
                                    0,
                                    {
                                        "product_id": line_product.id,
                                        "line_uom_id": line_product.uom_id.id,
                                        "line_quantity": float(sheet.cell(row, destination_qty_rno).value),
                                    },
                                )
                            )
                        break

                assembly_values.update({"kit_line_ids": assembly_lines})
                assembly_id = self.env["kit.assembly"].create(assembly_values)
                assembly_id._onchange_product_id_uom()
                assembly_id._onchange_warehouse_id()
