from odoo import fields, models, api, _
from datetime import date
from datetime import timedelta
from odoo.exceptions import UserError
import base64


class LogisticScheduler(models.Model):
    _name = "logistic.scheduler"
    _description = "Logistic Scheduler"

    name = fields.Char(string="Name", required=True, copy=False)
    start_date = fields.Date(
        string="Start Date",
    )
    end_date = fields.Date(
        string="End Date",
    )
    logistics_id = fields.Many2one(
        comodel_name="bi.logistics.master",
        string="Logistics",
    )
    email_from = fields.Char(
        string="Email From",
    )
    email_to = fields.Char(
        string="Email To",
    )
    email_cc = fields.Char(
        string="Email CC",
    )

    def export_logistics_report(self):
        # EXCEL REPORT
        logistic_scheduler_id = self.env["logistic.scheduler"].search([], limit=1)
        if logistic_scheduler_id.email_to:
            logistic_scheduler_id.end_date = date.today()
            logistic_scheduler_id.start_date = logistic_scheduler_id.end_date - timedelta(weeks=2)
            if (
                logistic_scheduler_id.end_date
                and logistic_scheduler_id.start_date
                and logistic_scheduler_id.logistics_id
            ):
                data = {
                    "ids": logistic_scheduler_id.ids,
                    "model": logistic_scheduler_id._name,
                    "form": {
                        "start_date": logistic_scheduler_id.start_date,
                        "end_date": logistic_scheduler_id.end_date,
                        "logistics_id": logistic_scheduler_id.logistics_id.id,
                    },
                }
                attachments = []
                excel_report = self.env.ref("bi_logistics_report.action_scheduler_export_report")
                generated_excel_report = excel_report._render_xlsx(logistic_scheduler_id.id, data=data)
                data_record = base64.b64encode(generated_excel_report[0])
                ir_values = {
                    "name": "Logistic Report.xlsx",
                    "type": "binary",
                    "datas": data_record,
                    "store_fname": data_record,
                    "mimetype": "application/vnd.ms-excel",
                    "res_model": "logistic.scheduler",
                }
                attachment = self.env["ir.attachment"].sudo().create(ir_values)
                if attachment:
                    attachments.append(attachment.id)
                # PDF REPORT
                pdf_report_id = self.env.ref("bi_logistics_report.action_pdf_report")
                generated_pdf_report = pdf_report_id._render_qweb_pdf(logistic_scheduler_id.id, data=data)
                pdf_data_record = base64.b64encode(generated_pdf_report[0])
                ir_values = {
                    "name": "Logistic Report.pdf",
                    "type": "binary",
                    "datas": pdf_data_record,
                    "store_fname": pdf_data_record,
                    "mimetype": "application/pdf",
                    "res_model": "logistic.scheduler",
                }
                report_attachment = self.env["ir.attachment"].sudo().create(ir_values)
                if report_attachment:
                    attachments.append(report_attachment.id)

                # MAIL
                email_template = self.env.ref("bi_logistics_report.email_template_logistic")
                body_html = f"""
                    <p>
                        Dear Sir,
                        <br/>
                        Please find attached the processing charges and stats for period
                        {logistic_scheduler_id.start_date} - {logistic_scheduler_id.end_date}.
                        <br/>
                        Please check and circulate to all relevant parties.
                    </p>


                    """
                if logistic_scheduler_id.email_from and logistic_scheduler_id.email_to:
                    if email_template:
                        email_values = {
                            "email_to": logistic_scheduler_id.email_to,
                            "email_from": logistic_scheduler_id.email_from,
                            "body_html": body_html,
                            "email_cc": logistic_scheduler_id.email_cc,
                        }
                        email_template.attachment_ids = [(6, 0, attachments)]
                        email_template.send_mail(1, email_values=email_values, force_send=True)
                        email_template.attachment_ids = [(5, 0, 0)]

    @api.constrains("name")
    def _constraint_single_record(self):
        rec = self.env["logistic.scheduler"].search_count([])
        if rec > 1:
            raise UserError(_("Only one record is allowed"))
