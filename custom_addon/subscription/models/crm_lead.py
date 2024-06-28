# -*- coding: utf-8 -*-
from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    order = fields.Char(string='order id')

    _sql_constraints = [('order',
                         'unique(order)',
                         'Order_id must be a unique value')]
