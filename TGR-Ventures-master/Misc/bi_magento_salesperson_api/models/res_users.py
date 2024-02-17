from odoo import fields, api, _, models
import requests
import json


class Resusers(models.Model):
    _inherit = "res.users"

    magento_salesperson_id = fields.Char("Magento Salesperson ID")
