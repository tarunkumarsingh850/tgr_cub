from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_reason_id = fields.Many2one(
        "reason.code", config_parameter="bi_reason_code.sale_reason_id", string="Sale Reason Code"
    )
    purchase_reason_id = fields.Many2one(
        "reason.code", config_parameter="bi_reason_code.purchase_reason_id", string="Purchase Reason Code"
    )
