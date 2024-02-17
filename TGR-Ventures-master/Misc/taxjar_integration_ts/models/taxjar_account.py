from odoo import fields, api, models, _
from odoo.exceptions import ValidationError, UserError
import requests
import json
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class TaxjarAccount(models.Model):
    _name = "taxjar.account"
    _description = "TaxJar Account"

    _get_states = [("draft", "Draft"), ("confirm", "Confirmed")]

    name = fields.Char("Name", required=True)
    api_key = fields.Char("API Token")
    state = fields.Selection(_get_states, string="State", default="draft")
    state_ids = fields.Many2many(
        "res.country.state", "res_state_taxjar_rel", "taxjar_id", "state_id", string="Your States with Nexus"
    )
    refresh_rate_interval = fields.Integer(default=1, help="To use rate will update every x.")
    refresh_rate_interval_type = fields.Selection(
        [("minutes", "Minutes"), ("hours", "Hours"), ("days", "Days"), ("weeks", "Weeks"), ("months", "Months")],
        string="Interval Unit",
        default="hours",
    )
    tax_breakdown = fields.Boolean(
        "Apply Tax Breakdown", help="Used to apply taxes breakdown. e.g. city, state and country taxes in the line."
    )
    transaction_sync = fields.Boolean(
        "Transaction Sync?",
        default=True,
        help="If checked then automatically Order invoice and refund invoice transaction export Odoo to TaxJar.",
    )
    prod_environment = fields.Boolean(
        "Environment", default=True, help="Set to True if your credentials are certified for production."
    )
    default_invoice_tax_account_id = fields.Many2one(
        "account.account",
        "Default Invoice Tax Account",
        help="Used when creating a new tax to add account on Definition for invoice. e.g. Tax received on selected account.",
    )
    default_credit_tax_account_id = fields.Many2one(
        "account.account",
        "Default Credit Note Tax Account",
        help="Used when creating a new tax to add account on Definition for credit note. e.g. Tax deduct on selected account.",
    )
    company_id = fields.Many2one("res.company", "Company", required=True, default=lambda self: self.env.company)

    def toggle_prod_environment(self):
        """changed the environment sandbox to production or production to sandbox to move in the draft state"""
        for c in self:
            c.prod_environment = not c.prod_environment
            c.state = "draft"

    def reset_draft(self):
        """when clicked on reset button to move in the draft state"""
        self.ensure_one()
        # found = self.env['account.fiscal.position'].search([('taxjar_account_id','=',self.id)])
        # if found:
        #     raise ValidationError(_("You can not change state still referenced on fiscal positions %s" % found.mapped('name')))
        self.state = "draft"
        return True

    def account_confirm(self):
        """Send request to TaxJar for check connection Odoo to TaxJar"""
        if not self.api_key:
            raise ValidationError(_("TaxJar API token is empty!"))
        try:
            res = self.with_context(no_create=True)._send_request("categories/")
            self.state = "confirm"
        except requests.HTTPError as e:
            raise UserError("Unauthorized API Token!!")

        return {
            "effect": {
                "fadeout": "slow",
                "message": "Congratulation, Connection Successful.",
                "img_url": "/web/static/src/img/smile.svg",
                "type": "rainbow_man",
            }
        }

    def get_from_address(self, partner):
        if not partner:
            return {}
        return {
            "from_country": partner.country_id.code,
            "from_zip": partner.zip,
            "from_state": partner.state_id.code,
            "from_city": partner.city,
            "from_street": "{} {}".format(partner.street or "", partner.street2 or ""),
        }

    def get_to_address(self, partner):
        if not partner:
            return {}
        return {
            "exemption_type": partner.ts_exemption_type
            or partner.parent_id
            and partner.parent_id.ts_exemption_type
            or "non_exempt",
            "to_country": partner.country_id.code,
            "to_zip": partner.zip,
            "to_state": partner.state_id.code,
            "to_city": partner.city,
            "to_street": "{} {}".format(partner.street or "", partner.street2 or ""),
        }

    def get_nexus_addresses(self, partner):
        if not partner:
            return []
        return [
            {
                "country": partner.country_id.code,
                "zip": partner.zip,
                "state": partner.state_id.code,
                "city": partner.city,
                "street": "{} {}".format(partner.street or "", partner.street2 or ""),
            }
        ]

    def create_or_update_taxjar_rate(self, res, taxjar_category, rec_partner, shipping_partner):
        tax_id = self.env["account.tax"]
        tax_rec = res.get("tax", {})
        rate = round(tax_rec.get("rate", 0.0) * 100, 2)
        if rate:
            ts_exemption_type = (
                shipping_partner.ts_exemption_type
                or shipping_partner.parent_id
                and shipping_partner.parent_id.ts_exemption_type
                or "non_exempt"
            )
            jurisdictions = tax_rec.get("jurisdictions", {})
            state_code = jurisdictions.get("state", shipping_partner.state_id.code)
            country_code = jurisdictions.get("country", shipping_partner.country_id.code)
            jurisdictions.get("city", shipping_partner.city)
            state_id, country_id = self.get_state_and_zip_data(state_code, country_code)
            rate_id, tax_id = self.create_or_update_account_tax_taxjar_rate(
                taxjar_category,
                ts_exemption_type,
                rec_partner,
                shipping_partner.zip,
                state_id,
                country_id,
                rate,
                tax_rec,
            )
        return tax_id

    def get_and_update_tax_rate(self, taxjar_category, ts_exemption_type, from_partner, to_partner):
        """
        :param taxjar_category: taxjar category
        :param ts_exemption_type: type
        :param from_partner: (order)warehouse partner contact or (invoice)company contact
        :param to_partner: shipping partner
        :return: tax id(account tax), taxjar rate both are browsable
        """
        tax_rate_obj = self.env["taxjar.tax.rate"]
        tax_id = self.env["account.tax"].sudo()
        interval_date = relativedelta(**{self.refresh_rate_interval_type: self.refresh_rate_interval})
        ref_date = fields.Datetime.now() - interval_date
        tax_rate_id = tax_rate_obj.search(
            [
                ("ts_exemption_type", "=", ts_exemption_type),
                ("tx_category_id", "=", taxjar_category.id),
                ("from_state_id", "=", from_partner.state_id.id),
                ("from_country_id", "=", from_partner.country_id.id),
                ("from_zip", "=", from_partner.zip),
                ("state_id", "=", to_partner.state_id.id),
                ("country_id", "=", to_partner.country_id.id),
                ("name", "=", to_partner.zip),
                ("account_id", "=", self.id),
                ("sync_date", ">", ref_date),
                ("is_recalculate", "=", False),
            ],
            limit=1,
        )
        if tax_rate_id:
            if not self.tax_breakdown:
                tax_id = self.create_or_find_account_tax(tax_rate_id.tax_rate)
            else:
                tax_id = self.create_or_find_account_tax(tax_rate_id.city_tax_rate)
                tax_id += self.create_or_find_account_tax(tax_rate_id.state_tax_rate, taxes_ids=tax_id)
                tax_id += self.create_or_find_account_tax(tax_rate_id.county_tax_rate, taxes_ids=tax_id)
                tax_id += self.create_or_find_account_tax(tax_rate_id.special_tax_rate, taxes_ids=tax_id)
        return tax_id

    def apply_shipping_taxes(self, res, taxjar_category, rec_partner, shipping_partner):
        if res and res.get("tax", False) and res.get("tax", {}).get("freight_taxable", {}):
            return self.create_or_update_taxjar_rate(res, taxjar_category, rec_partner, shipping_partner)
        else:
            return self.env["account.tax"].sudo()

    def get_taxes(self, shipping_dict, taxjar_category, rec_partner, shipping_partner, is_shipping=False):
        decrease_taxamount = 0.0
        decrese_taxable_amount = 0.0
        ts_exemption_type = (
            shipping_partner.ts_exemption_type
            or shipping_partner.parent_id
            and shipping_partner.parent_id.ts_exemption_type
            or "non_exempt"
        )
        tax_id = self.env["account.tax"].sudo()
        if shipping_partner.state_id in self.state_ids:
            tax_id = self.get_and_update_tax_rate(taxjar_category, ts_exemption_type, rec_partner, shipping_partner)
            if not tax_id or is_shipping:
                req_data = {}
                req_data.update(self.get_from_address(rec_partner))
                req_data.update(self.get_to_address(shipping_partner))
                # req_data.update({'nexus_addresses':self.get_nexus_addresses(shipping_partner)})
                req_data.update(shipping_dict)
                res = self._send_request("taxes", json_data=req_data, method="POST")
                decrease_taxamount = (
                    res.get("tax")
                    and (res.get("tax").get("order_total_amount") != res.get("tax").get("taxable_amount"))
                    and res.get("tax").get("amount_to_collect")
                    or 0
                )
                decrese_taxable_amount = (
                    res.get("tax")
                    and (res.get("tax").get("order_total_amount") != res.get("tax").get("taxable_amount"))
                    and res.get("tax").get("taxable_amount")
                    or 0
                )
                if is_shipping:
                    return (
                        self.apply_shipping_taxes(res, taxjar_category, rec_partner, shipping_partner),
                        decrease_taxamount,
                        decrese_taxable_amount,
                    )
                else:
                    # decrease_taxamount = res.get('tax') and (res.get('tax').get('order_total_amount') != res.get('tax').get('taxable_amount')) and res.get('tax').get('amount_to_collect') or 0
                    # decrese_taxable_amount = res.get('tax') and (res.get('tax').get('order_total_amount') != res.get('tax').get('taxable_amount')) and res.get('tax').get('taxable_amount') or 0
                    tax_id = self.create_or_update_taxjar_rate(res, taxjar_category, rec_partner, shipping_partner)
        return tax_id, decrease_taxamount, decrese_taxable_amount

    def get_state_and_zip_data(self, state_code, country_code):
        state_obj = self.env["res.country.state"]
        country_obj = self.env["res.country"]
        country_id = country_obj.search([("code", "=", country_code)], limit=1)
        state_id = state_obj.search([("code", "=ilike", state_code), ("country_id", "=", country_id.id)], limit=1)
        if not state_id:
            state_id = state_obj.create({"name": state_code, "code": state_code, "country_id": country_id.id})
        return state_id, country_id

    def create_or_find_account_tax(self, rate, taxes_ids=False):
        taxes_ids = taxes_ids or self.env["account.tax"]
        account_tax_obj = self.env["account.tax"].sudo()
        company_id = self._context.get("company_id", False) or self.env.user.company_id.id
        tax_id = account_tax_obj.search(
            [
                ("amount_type", "=", "percent"),
                ("amount", "=", rate),
                ("type_tax_use", "=", "sale"),
                ("company_id", "=", company_id),
                ("id", "not in", taxes_ids.ids),
            ],
            limit=1,
        )
        if not tax_id and rate:
            tax_group_id = self.env["account.tax.group"].search([("name", "=", "Tax {}%".format(rate))])
            if not tax_group_id:
                tax_group_id = self.env["account.tax.group"].sudo().create({"name": "Tax {}%".format(rate)})
            tax_id = account_tax_obj.create(
                {
                    "name": "Tax {}%".format(rate),
                    "amount_type": "percent",
                    "description": "{}%".format(rate),
                    "tax_group_id": tax_group_id.id,
                    "amount": rate,
                }
            )
            repartition_line_ids = tax_id.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == "tax")
            repartition_line_ids.write({"account_id": self.default_invoice_tax_account_id})
            ref_repartition_line_ids = tax_id.refund_repartition_line_ids.filtered(
                lambda x: x.repartition_type == "tax"
            )
            ref_repartition_line_ids.write({"account_id": self.default_credit_tax_account_id})
        return tax_id

    def create_or_update_account_tax_taxjar_rate(
        self, taxjar_category, ts_exemption_type, rec_partner, zip_code, state_id, country_id, rate, tax_rec
    ):
        tax_rate_obj = self.env["taxjar.tax.rate"]
        breakdown = tax_rec.get("breakdown", {})
        city_rate = round(breakdown.get("city_tax_rate", 0.0) * 100, 2)
        state_rate = round(breakdown.get("state_tax_rate", 0.0) * 100, 2)
        county_tax_rate = round(breakdown.get("county_tax_rate", 0.0) * 100, 2)
        special_rate = round(breakdown.get("special_tax_rate", 0.0) * 100, 2)
        is_recalculate = tax_rec.get("order_total_amount") != tax_rec.get("taxable_amount") and rate and True or False

        rate_id = tax_rate_obj.search(
            [
                ("ts_exemption_type", "=", ts_exemption_type),
                ("tx_category_id", "=", taxjar_category.id),
                ("state_id", "=", state_id.id),
                ("country_id", "=", country_id.id),
                ("name", "=", zip_code),
                ("from_state_id", "=", rec_partner.state_id.id),
                ("from_country_id", "=", rec_partner.country_id.id),
                ("from_zip", "=", rec_partner.zip),
                ("account_id", "=", self.id),
            ]
        )
        if not rate_id:
            rate_id = tax_rate_obj.create(
                {
                    "ts_exemption_type": ts_exemption_type,
                    "tx_category_id": taxjar_category.id,
                    "state_id": state_id.id,
                    "country_id": country_id.id,
                    "name": zip_code,
                    "tax_rate": rate,
                    "city_tax_rate": city_rate,
                    "state_tax_rate": state_rate,
                    "county_tax_rate": county_tax_rate,
                    "special_tax_rate": special_rate,
                    "sync_date": fields.Datetime.now(),
                    "from_state_id": rec_partner.state_id.id,
                    "from_country_id": rec_partner.country_id.id,
                    "from_zip": rec_partner.zip,
                    "from_street": "{} {}".format(rec_partner.street, rec_partner.street2),
                    "account_id": self.id,
                    "is_recalculate": is_recalculate,
                }
            )
        else:
            rate_id.write({"tax_rate": rate, "sync_date": fields.Datetime.now(), "is_recalculate": is_recalculate})
        if not self.tax_breakdown:
            tax_id = self.create_or_find_account_tax(rate)
        else:
            tax_id = self.create_or_find_account_tax(city_rate)
            tax_id += self.create_or_find_account_tax(state_rate, taxes_ids=tax_id)
            tax_id += self.create_or_find_account_tax(county_tax_rate, taxes_ids=tax_id)
            tax_id += self.create_or_find_account_tax(special_rate, taxes_ids=tax_id)
        return rate_id, tax_id

    def taxjar_sync_categories(self):
        category_obj = self.env["taxjar.category"]
        res = self._send_request("categories/")
        for category in res.get("categories", []):
            exist = category_obj.search([("product_tax_code", "=", category.get("product_tax_code"))])
            if exist:
                category_obj.write(category)
            else:
                category_obj.create(category)
        return True

    def taxjar_sync_state(self):
        state_ids = self.env["res.country.state"]
        res = self._send_request("nexus/regions")
        for state in res.get("regions", []):
            country_id = self.env["res.country"].search([("code", "=", state.get("country_code"))], limit=1)
            state_ids += self.env["res.country.state"].search(
                [("code", "=", state.get("region_code")), ("country_id", "=", country_id.id)]
            )
        self.state_ids = state_ids

    def create_taxjar_logs(self, method, url, data, json_data, response):
        logs_obj = self.env["taxjar.logs"]
        log = logs_obj.create(
            {
                "req_param": data,
                "url": url,
                "account_id": self.id,
                "method": method,
                "json_data": json_data,
                "date": fields.Datetime.now(),
                "response_text": "Connection Successful." if self._context.get("no_create", False) else response,
            }
        )
        return log

    @api.model
    def _send_request(self, req_url="", data=None, json_data=None, method="GET"):
        if not self.api_key:
            raise ValidationError(_("TaxJar API token is empty!"))
        headers = {"Authorization": "Authorization: Bearer {}".format(self.api_key), "x-api-version": "2022-01-24"}
        message_text = ""
        response_text = ""
        api_url = (
            "https://api.taxjar.com/v2/{}".format(req_url)
            if self.prod_environment
            else "https://api.sandbox.taxjar.com/v2/{}".format(req_url)
        )
        try:
            if data:
                data = json.dumps(data)
            req = requests.request(
                method, api_url, params={"plugin": "teqstars"}, headers=headers, data=data, json=json_data
            )
            req.raise_for_status()
            response_text = req.text
        except requests.HTTPError as e:
            # raise UserError("From TaxJar : \n %s" % req.text)
            if 'status' in json.loads(req.text) and json.loads(req.text)['status'] == 400:
                message_text = "Taxjar is not created \n From TaxJar : \n %s" % req.text
            else:
                message_text = "Taxjar is Created Successfully"
            _logger.info(message_text)
            response_text = req.text
        response = json.loads(response_text) if response_text else {}
        self.create_taxjar_logs(method, api_url, data, json_data, response)
        return response
