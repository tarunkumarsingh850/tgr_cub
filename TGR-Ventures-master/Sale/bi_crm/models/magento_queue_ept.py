from odoo import models


class MagentoResPartnerEpt(models.Model):
    _inherit = "magento.res.partner.ept"

    def _prepare_partner_values(self, data, instance, **kwargs):
        values = super(MagentoResPartnerEpt, self)._prepare_partner_values(data, instance, **kwargs)
        if "website_id" in data:
            website = instance.magento_website_ids.filtered(
                lambda w: int(w.magento_website_id) == data.get("website_id")
            )
            values["website"] = website.name
        if "taxvat" in data:
            if data["taxvat"]:
                values["vat"] = data["taxvat"]
        if "custom_attributes" in data:
            for data1 in data["custom_attributes"]:
                if data1["attribute_code"] == "website_url":
                    values["customer_website"] = data1["value"]
                if data1["attribute_code"] == "mobile_phone_number":
                    values["mobile"] = data1["value"]
                if data1["attribute_code"] == "personal_proof":
                    values["personal_identification_no"] = data1["value"]
                    values["company_type"] = "company"
                    values["customer_code"] = data.get("id", False)
                if data1["attribute_code"] == "business_identification":
                    values["business_identification_no"] = data1["value"]
                    values["company_type"] = "company"
                    values["customer_code"] = data.get("id", False)
                if data1["attribute_code"] == "products_interested":
                    if data1["value"] == "Non Seeds":
                        values["product_type"] = "non_seed"
                    else:
                        values["product_type"] = "seed"
                
                if data1["attribute_code"] == "current_buyer":
                    values["current_buyer"] = data1["value"]
                if data1["attribute_code"] == "is_reselling":
                    is_reselling_val = True
                    if data1["value"] == "0":
                        is_reselling_val = False
                    values["is_reselling"] = is_reselling_val
                if data1["attribute_code"] == "reselling":
                    values["reselling"] = data1["value"]
                if data1["attribute_code"] == "is_automated_ordering":
                    is_automated_ordering_val = True
                    if data1["value"] == "0":
                        is_reselling_val = False
                    values["is_automated_ordering"] = is_automated_ordering_val
                if data1["attribute_code"] == "monthly_turnover":
                    values["monthly_turnover"] = data1["value"]
                if data1["attribute_code"] == "hear_about_us":
                    values["hear_about_us"] = data1["value"]
                if data1["attribute_code"] == "business_since":
                    values["business_since"] = data1["value"]
                if data1["attribute_code"] == "other_products_to_sell":
                    values["other_products_to_sell"] = data1["value"]
                if data1["attribute_code"] == "current_selling_area":
                    values["current_selling_area"] = data1["value"]
                if data1["attribute_code"] == "brand_interested":
                    values["brand_interested"] = data1["value"]
                if data1["attribute_code"] == "type_of_business":
                    values["type_of_business"] = data1["value"]
                if data1["attribute_code"] == "interested_in_banking":
                    interested_in_banking_val = True
                    if data1["value"] == "0":
                        interested_in_banking_val = False
                    values["interested_in_banking"] = interested_in_banking_val
                if data1["attribute_code"] == "sms_notify":
                    sms_notify_val = True
                    if data1["value"] == "0":
                        sms_notify_val = False
                    values["sms_notify"] = sms_notify_val
                if data1["attribute_code"] == "receive_tracking_sms":
                    receive_tracking_sms_val = True
                    if data1["value"] == "0":
                        receive_tracking_sms_val = False
                    values["receive_tracking_sms"] = receive_tracking_sms_val
                if data1["attribute_code"] == "receive_marketing_sms":
                    receive_marketing_sms_val = True
                    if data1["value"] == "0":
                        receive_marketing_sms_val = False
                    values["receive_marketing_sms"] = receive_marketing_sms_val
        if "extension_attributes" in data and 'company_attributes' in data["extension_attributes"]:
            for data1 in data["extension_attributes"]['company_attributes']:
                if data1 == 'company_id':
                    values["magento_company_id"] = data["extension_attributes"]['company_attributes'][data1]
        return values
