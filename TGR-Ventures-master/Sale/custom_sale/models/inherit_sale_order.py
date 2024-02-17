# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _set_priority_group(self):
        priority_group_rec = self.env['priority.group'].search([('check_priority', '=', True)])
        priority = priority_group_rec
        return priority

    priority_group_id = fields.Many2one('priority.group', string='Priority Group', tracking=1,
                                        default=_set_priority_group)