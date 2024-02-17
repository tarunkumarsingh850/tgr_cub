"""For Odoo Magento2 Connector Module"""
from odoo import models


class AccountTaxCode(models.Model):
    """Inherited account tax model to calculate tax."""

    _inherit = "account.tax"

    def get_tax_from_rate(self, rate, name, is_tax_included=False, website=False):
        """
        This method,base on rate it find tax in odoo.
        @return : Tax_ids
        @author: Haresh Mori on dated 10-Dec-2018
        """
        for precision in [0.001, 0.01]:
            tax_ids = self.with_context(active_test=False).search(
                [
                    ("price_include", "=", is_tax_included),
                    ("type_tax_use", "in", ["sale"]),
                    ("amount", ">=", rate - precision),
                    ("amount", "<=", rate + precision),
                    ("company_id", "=", website.company_id.id),
                    ("name", "=", name),
                ],
                limit=1,
            )
            if tax_ids:
                return tax_ids
            else:
                tax_group_id = self.env["account.tax.group"].search(
                    [("country_id", "=", website.company_id.country_id.id)], limit=1
                )
                tax = self.create(
                    {
                        "price_include": is_tax_included,
                        "type_tax_use": "sale",
                        "amount": rate,
                        "company_id": website.company_id.id,
                        "name": name,
                        "tax_group_id": tax_group_id.id,
                        "country_id": website.company_id.country_id.id,
                    }
                )
                return tax
                # raise UserError(_(f"Tax {name} not found for company {website.company_id.name}"))

        return self
