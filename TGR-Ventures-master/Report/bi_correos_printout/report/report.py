from odoo import api, models
from datetime import datetime


class CorreosReport(models.AbstractModel):
    _name = "report.bi_correos_printout.correos_pdf_report"

    @api.model
    def _get_report_values(self, wizard, data):
        start_date = data["form"]["start_date"]
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = data["form"]["end_date"]
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        data["form"]["company_id"]
        wizard_carrier_id = data["form"]["carrier_id"]

        carrier_id = self.env["delivery.carrier"].search([("id", "=", wizard_carrier_id)])
        picking_ids = self.env["stock.picking"].search(
            [
                ("carrier_id", "=", carrier_id.id),
                ("date_done", ">=", start_date),
                ("date_done", "<=", end_date),
                ("state", "=", "done"),
            ]
        )

        logo_carried_id = False
        logo_carried_id = carrier_id.correos_log

        pickings = []
        total_qty = 0
        total_weight = 0
        for pick in picking_ids:
            qty = 0
            qty = sum(pick.move_line_ids_without_package.mapped("qty_done"))
            total_qty += qty
            total_weight += pick.weight
            val = {
                "name": pick.name,
                "origin": pick.origin,
                "tracking_ref": pick.carrier_tracking_ref,
                "partner": pick.partner_id.name,
                "street": pick.partner_id.street,
                "street2": pick.partner_id.street2,
                "city": pick.partner_id.city,
                "state": pick.partner_id.state_id.name,
                "country": pick.partner_id.country_id.name,
                "weight": pick.weight,
                "qty": qty,
            }
            pickings.append(val)

        # BARCODE
        md = "MD"
        cccc = False
        ee = False
        aaaammdd = False
        hhmmss = False
        nn = False

        if carrier_id.correos_labeller_code:
            cccc = carrier_id.correos_labeller_code
        if carrier_id.canal_de_pre_registro:
            ee = carrier_id.canal_de_pre_registro

        today = datetime.now()
        format = "%Y%m%d"
        aaaammdd = today.strftime(format)

        format = "%H%M%S"
        hhmmss = today.strftime(format)

        if carrier_id.correos_seq:
            nn = carrier_id.correos_seq
            carrier_id.correos_seq = carrier_id.correos_seq + 1

        barcode = False
        barcode = md + str(cccc) + str(ee) + str(aaaammdd) + str(hhmmss) + str(nn)
        carrier_id.correos_barcode = barcode

        return {
            "start_date": start_date.strftime("%d-%m-%Y"),
            "end_date": end_date.strftime("%d-%m-%Y"),
            "vals": pickings,
            "carrier": carrier_id.name,
            "logo_carried_id": logo_carried_id,
            "docs": self,
            "total_qty": total_qty,
            "total_weight": total_weight,
            "barcode": barcode,
        }
