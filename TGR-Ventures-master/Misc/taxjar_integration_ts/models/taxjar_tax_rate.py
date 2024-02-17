from odoo import fields, models


class TaxjarTaxRate(models.Model):
    _name = "taxjar.tax.rate"
    _description = "TaxJar Tax Rate"

    _get_ts_exemption_type = [
        ("wholesale", "Wholesales Or Resale Exempt"),
        ("government", "Government Entity Exempt"),
        ("other", "Entity Exempt"),
        ("non_exempt", "Not Exempt"),
    ]

    name = fields.Char("Zip", required=True)
    tax_rate = fields.Float("Tax Rate")
    account_id = fields.Many2one("taxjar.account", "Account")
    city_tax_rate = fields.Float("City Tax Rate(%)")
    state_tax_rate = fields.Float("State Tax Rate(%)")
    county_tax_rate = fields.Float("County Tax Rate(%)")
    special_tax_rate = fields.Float("Special Tax Rate(%)")
    sync_date = fields.Datetime("Last Sync Date")
    tx_category_id = fields.Many2one("taxjar.category", "TaxJar Category")
    ts_exemption_type = fields.Selection(
        _get_ts_exemption_type,
        default="non_exempt",
        string="TaxJar Exempt Type",
        help="This values used while calculating order taxes and invoice upload to TaxJar for this partner.",
    )
    is_recalculate = fields.Boolean("Is ReCalculate", help="This field use to recalculate taxes for some categories.")
    ##To Address Date
    state_id = fields.Many2one("res.country.state", "State")
    country_id = fields.Many2one("res.country", "Country")
    street = fields.Char("Street")

    ##From Address Data
    from_state_id = fields.Many2one("res.country.state", "From State")
    from_country_id = fields.Many2one("res.country", "From Country")
    from_street = fields.Char("From Street")
    from_zip = fields.Char("From Zip")
