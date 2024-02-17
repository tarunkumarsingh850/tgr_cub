from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    _get_ts_exemption_type = [
        ("wholesale", "Wholesales Or Resale Exempt"),
        ("government", "Government Entity Exempt"),
        ("other", "Entity Exempt"),
        ("non_exempt", "Not Exempt"),
    ]
    ts_exemption_type = fields.Selection(
        _get_ts_exemption_type,
        default="non_exempt",
        string="TaxJar Exempt Type",
        help="This values used while calculating order taxes and invoice upload to TaxJar for this partner.",
    )
