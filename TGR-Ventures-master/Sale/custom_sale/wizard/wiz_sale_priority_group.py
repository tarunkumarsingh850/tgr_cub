# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError, ValidationError

class WizardSalePriorityGroupRepot(models.TransientModel):
    _name = 'wizard.sale.priority.group.report'
    _description = 'PDF Report'

    date_from = fields.Date(string="Start Date", default=datetime.today() - timedelta(days = 1))
    date_to = fields.Date(string="End Date", default=datetime.today() - timedelta(days = 1))

    def action_print_sale_priority_group_report(self):
        domain = []
        date_from = self.date_from
        if date_from:
            domain += [('date_order', '>=', date_from)]
        date_to = self.date_to
        if date_to:
            domain += [('date_order', '<=', date_to)]
        sale_order = self.env['sale.order'].search(domain)
        order_list = []
        for rec in sale_order:
            vals = {
                'order_number': rec.name,
                'date_order': rec.date_order,
                'priority_group_id': rec.priority_group_id.name
            }
            order_list.append(vals)
        data = {
            'form_data': self.read()[0],
            'sale_order': order_list
        }
        return self.env.ref('custom_sale.action_report_priority_group').report_action(self, data=data)
