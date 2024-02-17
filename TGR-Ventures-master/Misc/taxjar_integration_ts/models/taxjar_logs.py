from odoo import fields, models, api, _


class TaxJarLog(models.Model):
    _name = "taxjar.logs"
    _description = "TaxJar Logs"
    _order = "name desc"

    name = fields.Char("Name")
    req_param = fields.Char("Request Data")
    response_text = fields.Text("Response")
    date = fields.Datetime("Date")
    url = fields.Char("URL")
    account_id = fields.Many2one("taxjar.account", "Account")
    method = fields.Char("Method")
    json_data = fields.Char("Json Data")

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            if "company_id" in vals:
                vals["name"] = self.env["ir.sequence"].with_context(force_company=vals["company_id"]).next_by_code(
                    "taxjar.logs"
                ) or _("New")
            else:
                vals["name"] = self.env["ir.sequence"].next_by_code("taxjar.logs") or _("New")
        return super(TaxJarLog, self).create(vals)
