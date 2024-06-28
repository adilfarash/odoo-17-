# -*- coding: utf-8 -*-
from odoo import api, fields, models, Command


class BillingSchedule(models.Model):
    _name = 'billing.schedule'
    _description = 'Billing Schedule'
    _inherit = 'mail.thread'

    name = fields.Char(help='Add a name', required=True)
    simulation = fields.Boolean(default=True)
    period = fields.Date(help='Add period date')
    restrict_customer_ids = fields.Many2many(comodel_name='res.partner')
    active = fields.Boolean(default=True)
    recurring_subscription_ids = fields.Many2many(comodel_name='recurring.subscription',
                                                  help='Add recurring subscription')
    recurring_subscriptions_ids = fields.Many2many(comodel_name='recurring.subscription',
                                                   compute='_compute_recurring_subscriptions_ids')
    subscription_count = fields.Integer(compute='_compute_subscription_count')
    credit_ids = fields.Many2many(comodel_name='recurring.credit')
    credits_ids = fields.Many2many(comodel_name='recurring.credit', compute='_compute_credits_ids')
    invoice_count = fields.Integer(compute='_compute_invoice')
    state = fields.Selection(selection=[('invoiced', 'Invoiced'),
                                        ('draft', 'Draft')
                                        ], default='draft')

    def _compute_invoice(self):
        """taking count of invoice"""
        self.invoice_count = self.env['account.move'].search_count([('invoice_line_ids.name', '=', self.name)])

    @api.depends('recurring_subscription_ids')
    def _compute_recurring_subscriptions_ids(self):
        """Only allows 'confirm' state in recurring subscription"""
        for rec in self:
            record_subscription = self.env['recurring.subscription'].search([('state', '=', 'confirm')]).ids
            rec.recurring_subscriptions_ids = [fields.Command.set(record_subscription)]

    @api.depends('credit_ids')
    def _compute_credits_ids(self):
        """Only allows 'confirm' state in recurring credit"""
        for rec in self:
            record_credit = self.env['recurring.credit'].search([('state', '=', 'confirm')]).ids
            rec.credits_ids = [fields.Command.set(record_credit)]

    def _compute_subscription_count(self):
        """calculates button"""
        for record in self:
            record.subscription_count = 0
            if record.recurring_subscription_ids:
                record.subscription_count = len(record.recurring_subscription_ids)

    @api.onchange('recurring_subscription_ids')
    def _onchange_recurring_subscription_ids(self):
        """adding credit or linking credit"""
        for record in self.recurring_subscription_ids:
            record = record._origin
            count = self.env['recurring.credit'].search([('recurring_subscription_id', '=', record.id),
                                                         ('state', '=', 'confirm')
                                                         ])
            self.credit_ids = [fields.Command.link(value.id) for value in count]

    def create_invoice(self):
        """creating invoice"""
        for record in self.recurring_subscription_ids:
            for rec in self.credit_ids.recurring_subscription_id:
                total = 0
                if rec.id == record.id:
                    credit = self.env['recurring.credit'].search(
                        [('recurring_subscription_id', '=', record.order)], order='id ASC')
                    credit_value = credit.filtered(
                        lambda line: line.state == 'confirm').mapped('credit_amount')
                    if credit_value:
                        amount = max(credit_value)
                        if record.recurring_amount >= amount:
                            total = record.recurring_amount - amount
                        break
                total = record.recurring_amount
            self.env['account.move'].create([
                {
                    'move_type': 'out_invoice',
                    'invoice_date': self.period,
                    'partner_id': record.customer_id.id,
                    'currency_id': 1,
                    'invoice_line_ids': [
                        Command.create({
                            'product_id': record.product_id.id,
                            'name': self.name,
                            'quantity': 1,
                            'price_unit': total,
                        }),
                    ],
                },
            ])
        self.write({
            'active': False,
            'state': 'invoiced'
        })

    def action_get_record(self):
        """subscription button(views and form)"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'subscription',
            'view_mode': 'tree',
            'res_model': 'recurring.subscription',
            'domain': [('id', 'in', self.recurring_subscription_ids.ids)],
        }

    def get_invoice_action(self):
        """invoice button (view and form)"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'invoice',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': self.env.ref('account.view_move_tree', False).id,
            'views': [(self.env.ref('account.view_move_tree', False).id, 'tree'), (False, 'form')],
            'domain': [('invoice_line_ids.name', '=', self.name)]
        }
