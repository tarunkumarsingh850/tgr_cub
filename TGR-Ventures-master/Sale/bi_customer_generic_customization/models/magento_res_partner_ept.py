from odoo import models


class MagentoResPartnerEpt(models.Model):
    _inherit = "magento.res.partner.ept"
    _description = "Magento Res Partner Ept"

    def _create_odoo_partner(self, data, instance):
        res = super(MagentoResPartnerEpt, self)._create_odoo_partner(data, instance)
        magento_store = data.get("store_view") or self.env["magento.storeview"].search([('magento_storeview_id','=',data.get("store_id"))], limit=1)
        website_id = magento_store.magento_website_id
        # website = data.get("website_id", False)
        # website_id = self.env['magento.website'].browse(website)
        if website_id:
            required_class = (
                self.env["customer.class"].search([]).filtered(lambda l: website_id.id in l.website_ids.ids).id
            )
            required_class_id = (
                self.env["customer.class"].search([]).filtered(lambda l: website_id.id in l.website_ids.ids)
            )

            res.customer_class_id = required_class
            if required_class_id and required_class_id.is_wholesales:
                companies = website_id.company_id
                account_type = self.env["account.account.type"].search([("type", "=", "receivable")], limit=1)
                for company in companies:
                    previous_code = self.env["account.account"].search(
                        [
                            ("code", "like", required_class_id.receivable_account_code_prefix),
                            ("company_id", "=", website_id.company_id.id),
                            ("user_type_id", "=", account_type.id),
                        ],
                        order="code desc",
                        limit=1,
                    )
                    if not previous_code:
                        code = f"{required_class_id.receivable_account_code_prefix}{'1'.zfill(6)}"
                    else:
                        old_suffix = previous_code.code[len(required_class_id.receivable_account_code_prefix) :]
                        new_suffix = f"{int(old_suffix) + 1}"
                        code = f"{required_class_id.receivable_account_code_prefix}{new_suffix.zfill(6)}"
                    s_code = self.env["account.account"].sudo().search([('code','=',code)])
                    if s_code:
                        new_suffix = f"{int(code) + 1}"
                        code = f"{required_class_id.receivable_account_code_prefix}{new_suffix.zfill(6)}"
                    else:
                        code = code
                    account_vals = {
                        "code": code,
                        "name": f"{res.name} Receivable Account",
                        "company_id": company.id,
                        "user_type_id": account_type.id,
                        "reconcile": True,
                    }
                    self.env["account.account"].sudo().create(account_vals)
        return res
