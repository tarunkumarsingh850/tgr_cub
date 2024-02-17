from odoo import models, api, fields, _


class EcommerceApiLog(models.Model):
    _name = "ecommerce.api.log"
    _order = "name desc"
    _description = "Ecommerce API Log"

    name = fields.Char("Reference", copy=False, readonly=True, default=lambda x: _("New"))
    request_date = fields.Datetime("Date", default=fields.Datetime.now)
    state = fields.Selection(
        [
            ("none", "None"),
            ("success", "Success"),
            ("failed", "Failed"),
        ],
        default="none",
    )
    status_message = fields.Text("Status Message", readonly=True)
    body = fields.Text("JSON body", readonly=True)
    sale_order_ids = fields.Many2many("sale.order", string="Sale Orders")
    type = fields.Selection([("api", "API"), ("xml", "XML"), ("csv", "CSV")], string="SO Created From")
    file_name = fields.Char(
        "File Name", help="If sale order is creating from xml file, this field will store " "the file name with path"
    )

    @api.model
    def create(self, vals):
        """
        @override - Adding sequence
        """
        if not vals.get("name") or vals["name"] == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("ecommerce.api.log") or _("New")
        return super(EcommerceApiLog, self).create(vals)

    def create_log(self, data, response, sale_order_ids, so_creation_type, file_name):
        """
        Create log with the response
        """
        state = "success" if ("success" in response) else "failed"
        self.create(
            {
                "state": state,
                "status_message": response,
                "body": data,
                "sale_order_ids": [(4, x.id) for x in sale_order_ids] if sale_order_ids else False,
                "type": so_creation_type,
                "file_name": file_name,
            }
        )
