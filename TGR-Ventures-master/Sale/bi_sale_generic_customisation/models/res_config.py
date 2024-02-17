from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fraud_score = fields.Integer("Fraud Score", config_parameter="bi_sale_generic_customisation.fraud_score")