from odoo import models
from odoo.http import request
from datetime import date, timedelta


class UpdateStockPriceExcelRpt(models.AbstractModel):
    _name = "report.bi_update_stock_price.update_stock_data_export"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet("Stock Update")
        sheet.set_column("A:A", 40)
        sheet.set_column("B:B", 30)
        sheet.set_column("C:C", 20)
        sheet.set_column("D:D", 20)
        sheet.write("A1", "sku")
        sheet.write("B1", "source_code")
        sheet.write("C1", "quantity")
        sheet.write("D1", "status")
        instance = request.env["magento.instance"].sudo().search([], limit=1)
        last_date = instance.last_update_stock_time
        if not last_date:
            last_date = date.today() - timedelta(days=1)
        product = self.env["product.product"]
        product_ids = product.get_products_based_on_movement_date_ept(last_date, instance.company_id)
        m_product = self.env["magento.product.product"]
        locations = self.env["stock.location"].search(
            [("usage", "=", "internal"), ("magento_location", "=", lines.magento_location_id.magento_location_code)]
        )
        row = 2
        for location in locations:
            magento_location = location.magento_location
            product_stock = m_product.get_magento_product_stock_ept(instance, product_ids, location.warehouse_id)
            for p_id in product_stock.keys():
                p_record = product.browse(p_id)
                sheet.write("A%s" % row, p_record.default_code)
                sheet.write("B%s" % row, magento_location)
                sheet.write("C%s" % row, product_stock[p_id])
                sheet.write("D%s" % row, 1)
                row += 1
