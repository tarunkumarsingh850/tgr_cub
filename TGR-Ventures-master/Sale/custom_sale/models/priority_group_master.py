# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PriorityGroup(models.Model):
    _name = 'priority.group'
    _description = 'priority.group'

    name = fields.Char(string='Name')
    check_priority = fields.Boolean(string='Default Priority Group')

    @api.constrains('check_priority')
    def _check_name(self):
        priority_group_rec = self.env['priority.group'].search(
            [('check_priority', '=', True)])
        if priority_group_rec and len(priority_group_rec) > 1:
            raise ValidationError(_('You cannot select more than one priority group'))