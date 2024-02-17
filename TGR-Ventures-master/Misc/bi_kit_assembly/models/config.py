from odoo import fields, models


class ResConfig(models.TransientModel):
    _inherit = "res.config.settings"

    journal_id = fields.Many2one(
        "account.journal", config_parameter="bi_kit_assembly.journal_id", string="Journal", required="True" , company_dependent=True,
    )

    account_assembly_id = fields.Many2one(
        "account.account",
        string="Inventory Account",
        required="True",
        config_parameter="bi_kit_assembly.account_assembly_id",
        company_dependent=True,
    )
