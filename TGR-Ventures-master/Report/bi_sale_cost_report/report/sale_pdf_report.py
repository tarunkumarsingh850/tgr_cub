from odoo import api, models


class PDFSale(models.AbstractModel):
    _name = "report.bi_dynamic_sale_report.report_sale_dynamic_pdf"

    @api.model
    def _get_report_values(self, wizard, data):
        domain = []
        if data["form"]["date_from"]:
            domain.append(("date_order", ">=", data["form"]["date_from"]))
        if data["form"]["date_to"]:
            domain.append(("date_order", "<=", data["form"]["date_to"]))
        # if data["form"]["partner_id"]:
        #         domain.append(("partner_id", "=",data["form"]["partner_id"]))
        values = []
        record = self.env["sale.order"].search(domain)
        for each in record:
            values.append(
                {
                    "type": each.order_type_id.name if each.order_type_id else "",
                    "ref": each.name,
                    "order_date": each.date_order,
                    "status": each.state.capitalize(),
                    "currency": each.currency_id.name if each.currency_id else "",
                    "cus_id": each.partner_id.customer_code,
                    "cus_name": each.partner_id.name,
                    "payment_method": each.payment_term_id.name if each.payment_term_id else "",
                    "warehouse": "",
                    "order_qty": 0,
                    "open_qty": 0,
                    "line_total": 0,
                    "open_amount": 0,
                }
            )
        return {
            "lines": sorted(values, key=lambda i: i["ref"], reverse=True),
        }
