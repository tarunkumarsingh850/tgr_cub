from odoo import fields, models, api, _
import requests
import json


class ResPartner(models.Model):
    _inherit = 'res.partner'



    def update_magento_salesperson(self):
        """ Update Magento salesperson id for users who have a valid magento user id"""
        instance = self.env["magento.instance"].sudo().search([], limit=1)
        magento_url = instance and instance.magento_url or False
        if magento_url:
            new_headers = {
                "Accept": "*/*",
                "Content-Type": "application/json",
                "User-Agent": "My User Agent 1.0",
                "Authorization": "Bearer {}".format(instance.access_token),
            }
            for rec in self.search([('magento_company_id','!=',False)]):
                api_url = "{}/rest/V1/company/{}".format(magento_url, rec.magento_company_id)
                label_response = requests.get(api_url, headers=new_headers)
                label_response = label_response.json()
                if 'sales_representative_id' in label_response:
                    salesperson_value = label_response['sales_representative_id'] or {}
                    user_id = self.env['res.users'].search([('magento_salesperson_id','=', salesperson_value)],limit=1)
                    rec.user_id = user_id and user_id.id or False