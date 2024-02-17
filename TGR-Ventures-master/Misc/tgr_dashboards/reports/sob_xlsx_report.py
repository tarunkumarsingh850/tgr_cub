from odoo import models, fields, _ , api
from datetime import date, datetime
import xlwt
from io import BytesIO
import base64
from . import xls_format


class SOBPrintSuccessBox(models.TransientModel):
    _name = "sob.print.success.box"
    _description = "sob.print.success.box"

    file = fields.Binary("File", readonly=True)
    fname = fields.Char("Text")



    def print_sob_xls_report(self,data):
    
        workbook = xlwt.Workbook()


        sheet = workbook.add_sheet("Test")
        header_tstyle_c = xls_format.font_style(
            position="center", bold=1, border=1, fontos="black", font_height=180, color="teal"
        )
        header_tstyle_d = xls_format.font_style(
            position="center", bold=1, border=1, fontos="black", font_height=180, color="grey"
        )

        sheet.write(3,0,'SKU', header_tstyle_c)
        sheet.write(3,1,'Brand', header_tstyle_c)
        sheet.write(3,2,'Name', header_tstyle_c)
        sheet.write(3,3,'Inventory \nValue', header_tstyle_c)
        sheet.write(3,4,'Ideal \nInventory Value', header_tstyle_c)
        sheet.write(3,5,'Inventory Value \nvs.\n Ideal Inventory Value', header_tstyle_c)
        sheet.write(3,6,'Total Purchases', header_tstyle_c)
        sheet.write(3,7,'Total Purchases \nQty', header_tstyle_c)
        sheet.write(3,8,'Total Sales', header_tstyle_c)
        sheet.write(3,9,'Total Profit', header_tstyle_c)
        sheet.write(3,10,'Total Sales \nQty', header_tstyle_c)
        sheet.write(3,11,'Cost \nof \nSales', header_tstyle_c)
        sheet.write(3,12,'Purchases\n vs\n Cost of Sales', header_tstyle_c)
        sheet.write(3,13,'Profit Margin', header_tstyle_c)
        sheet.write(3,14,'Sell Through', header_tstyle_c)
        sheet.write(3,15,'ABC \nClassification', header_tstyle_c)
        sheet.write(3,16,'Pack Size', header_tstyle_c)
        sheet.write(3,17,'Sex', header_tstyle_c)
        sheet.write(3,18,'Flowering Type', header_tstyle_c)
        sheet.write(3,19,'Creation Date', header_tstyle_c)
        sheet.write(3,20,'Last Sale Date', header_tstyle_c)
        sheet.write(3,21,'Last Receipt \nor \nKit Assembly Date', header_tstyle_c)
        sheet.write(3,22,'Product \nGroup/Category', header_tstyle_c)

        sheet.row(3).height = 256 * 3
        sheet.col(0).width = 256 * 23
        sheet.col(1).width = 256 * 25
        sheet.col(2).width = 256 * 35
        sheet.col(4).width = 256 * 20
        sheet.col(5).width = 256 * 20
        sheet.col(6).width = 256 * 20
        sheet.col(7).width = 256 * 20
        sheet.col(12).width = 256 * 20
        sheet.col(15).width = 256 * 20
        sheet.col(18).width = 256 * 20
        sheet.col(19).width = 256 * 20
        sheet.col(20).width = 256 * 20
        sheet.col(21).width = 256 * 20
        sheet.col(22).width = 256 * 20
        row = 4
        if data["lines"]:
            for lines in data.get("lines"):
                sheet.row(row).height = 256
                column = 0
                sheet.write(row, column, lines.get('sku'))
                column+=1
                sheet.write(row, column, lines.get('brand_name'))
                column+=1
                sheet.write(row, column, lines.get('name'))
                column+=1
                sheet.write(row, column, lines.get('inventory_value'))
                column+=1
                sheet.write(row, column, lines.get('ideal_inventory_value'))
                column+=1
                sheet.write(row, column, lines.get('inv_value_v_ideal_value'))
                column+=1
                sheet.write(row, column, lines.get('total_purchases'))
                column+=1
                sheet.write(row, column, lines.get('total_purchase_qty'))
                column+=1
                sheet.write(row, column, lines.get('total_sales'))
                column+=1
                sheet.write(row, column, lines.get('total_profit'))
                column+=1
                sheet.write(row, column, lines.get('total_sales_qty'))
                column+=1
                sheet.write(row, column, lines.get('cost_of_sales'))
                column+=1
                sheet.write(row, column, lines.get('purchase_vs_cost_of_sales'))
                column+=1
                sheet.write(row, column, lines.get('profit_margin'))
                column+=1
                sheet.write(row, column, lines.get('sell_through'))
                column+=1
                sheet.write(row, column, lines.get('abc_classification'))
                column+=1
                sheet.write(row, column, lines.get('pack_size'))
                column+=1
                sheet.write(row, column, lines.get('sex'))
                column+=1
                sheet.write(row, column, lines.get('flower_type'))
                column+=1
                sheet.write(row, column, lines.get('create_date'))
                column+=1
                sheet.write(row, column, lines.get('last_sale_date'))
                column+=1
                sheet.write(row, column, lines.get('last_receipt_or_kit_assembly_date'))
                column+=1
                sheet.write(row, column, lines.get('product_group_category'))
                row+=1
            
            column = 2
            sheet.write(row, column, "Total", header_tstyle_d)
            column+=1
            sheet.write(row, column, data["total"]["total_inv_val"], header_tstyle_d)
            column+=1
            sheet.write(row, column, data["total"]["total_ideal_inv_val"], header_tstyle_d)
            column+=1
            sheet.write(row, column, data["total"]["total_inv_val_v_ideal_inv_val"], header_tstyle_d)
            column+=1
            sheet.write(row, column, data["total"]["total_purchases"], header_tstyle_d)
            column+=1
            sheet.write(row, column, data["total"]["total_purchase_qty"], header_tstyle_d)
            column+=1
            sheet.write(row, column, data["total"]["total_sales"], header_tstyle_d)
            column+=1
            sheet.write(row, column, data["total"]["total_profit"], header_tstyle_d)
            column+=1
            sheet.write(row, column, data["total"]["total_sales_qty"], header_tstyle_d)
            column+=1
            sheet.write(row, column, data["total"]["total_cost_of_sales"], header_tstyle_d)
            column+=1
            sheet.write(row, column, data["total"]["total_purchases_vs_cost_of_sales"], header_tstyle_d)
            column+=1
            sheet.write(row, column, data["total"]["profit_margin_total"], header_tstyle_d)
            column+=1
            sheet.write(row, column, data["total"]["sell_through_total"], header_tstyle_d)

        stream = BytesIO()
        workbook.save(stream)

        export_obj = self.env["sob.print.success.box"]
        res_id = export_obj.create(
            {"file": base64.encodestring(stream.getvalue()), "fname": "SOB Report.xls"}
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/binary/download_sob_document?model=sob.print.success.box&field=file&id=%s&filename=SOB Print.xls"
            % (res_id.id),
            "target": "new",
        }