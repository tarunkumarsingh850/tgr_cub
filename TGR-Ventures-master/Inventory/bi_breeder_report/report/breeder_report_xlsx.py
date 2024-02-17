from odoo import models, fields
from datetime import timedelta
from odoo.http import request


class BrandBreederReportXlsx(models.AbstractModel):
    _name = "report.bi_breeder_report.report_brand_breeder_xlsx"
    _description = "Brand Breeder XLSX Report"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, record):
        worksheet = workbook.add_worksheet("Brand Breeder Report")

        header_format = workbook.add_format({
            'align': 'center',
            'bold': 1,
            'font_size': 16,
            'font': 'Liberation Serif'
        })
        worksheet.set_row(0, 25)
        worksheet.set_column("A:A", 45)
        worksheet.set_column("B:B", 30)
        worksheet.set_column("B:B", 30)
        worksheet.set_column("C:C", 30)
        worksheet.set_column("D:D", 30)
        worksheet.set_column("E:E", 30)
        worksheet.write("A1", "Product", header_format)
        worksheet.write("B1", "Breed", header_format)
        worksheet.write("C1", "Available Quantity", header_format)
        worksheet.write("D1", "On-hand Quantity", header_format)
        worksheet.write("E1", "Ideal Quantity", header_format)

        product_ids = self.env['product.product'].search([('product_breeder_id', 'in', record.brand_id.ids)]).sorted(key=lambda p: p.product_breeder_id.id)
        row = 2
        domain = [("warehouse_id", "=", record.warehouse_id.id)] if record.warehouse_id else []
        for product in product_ids:
            worksheet.write("A%s" % row, product.name)
            worksheet.write("B%s" % row, product.product_breeder_id.breeder_name)
            worksheet.write("C%s" % row, product.virtual_available)
            worksheet.write("D%s" % row, product.qty_available)

            today_date = fields.Date.today()
            total_delivered_quantity = 0
            for i in range(12, 0, -1):
                query_domain = list(domain)
                start_period_date = today_date - timedelta(days=i * 7)
                end_period_date = start_period_date + timedelta(days=7)
                qty_delivered = 0
                query_domain.extend([
                                    ("product_id", "=", product.id),
                                    ("order_id.state", "in", ("done", "sale")),
                                    ("order_id.date_order", ">=", start_period_date),
                                    ("order_id.date_order", "<=", end_period_date)
                                ])
                sale_line_ids = self.env["sale.order.line"].search(query_domain)
                qty_delivered = sum(sale_line_ids.mapped("qty_delivered"))
                total_delivered_quantity += qty_delivered

            # average = (total_delivered_quantity / avg_weeks) if avg_weeks else 0
            # ideal_qty = average * avg_weeks_for_sale
            average = (total_delivered_quantity / 12)
            ideal_qty = average * 5
            worksheet.write("E%s" % row, round(ideal_qty,2))

            row += 1