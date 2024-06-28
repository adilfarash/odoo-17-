# -*- coding: utf-8 -*-
import datetime

from odoo import api, Command, fields, models, _, re
from odoo.exceptions import ValidationError


class RecurringSubscription(models.Model):
    _name = 'recurring.subscription'
    _description = 'Recurring Subscription'
    _rec_name = 'order'
    _inherit = 'mail.thread'

    order = fields.Char(readonly=True, default=lambda self: _('New'))
    name = fields.Char(help="Enter the name", required=True)
    establishment_id = fields.Char(related="customer_id.establishment_id", help="Enter the Establishment_id",
                                   readonly=False)
    date = fields.Date(default=fields.Date.today(), help="Enter the date")
    due_date = fields.Date(default=fields.Date.add(fields.Date.today(), days=15))
    company_id = fields.Many2one(comodel_name="res.company", help="Add company name",
                                 default=lambda self: self.env.company.id)
    next_billing = fields.Date(default=fields.Date.add(fields.Date.today(), days=90))
    is_lead = fields.Boolean(default="True", help="Is it a lead")
    customer_id = fields.Many2one(comodel_name='res.partner', help="Enter customer")
    description = fields.Text(help="Add description")
    terms_and_conditions = fields.Html()
    billing_schedule_ids = fields.Many2many(comodel_name='billing.schedule')
    product_id = fields.Many2one('product.product', help="Name the product")
    recurring_amount = fields.Float(help="The amount that must be paid")
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirm', 'Confirm'),
                                        ('done', 'Done'),
                                        ('cancel', 'Cancel')], default="draft", tracking=True, readonly=True)
    recurring_credit_ids = fields.Many2many(comodel_name='recurring.credit')
    recurring_credit_a_ids = fields.Many2many(comodel_name='recurring.credit',
                                              compute='_compute_recurring_credit_ids')

    @api.depends('recurring_credit_ids')
    def _compute_recurring_credit_ids(self):
        """adding many2 many use the search"""
        for rec in self:
            records_credit = self.env['recurring.credit'].search([('period_date',
                                                                   '<', rec.due_date)]).ids
            rec.recurring_credit_a_ids = [fields.Command.set(records_credit)]

    @api.onchange('establishment_id')
    def _onchange_establishment_id(self):
        """ onchange of establishment_id the partner will be added"""
        if self.establishment_id:
            customer = self.env['res.partner'].search([('establishment_id', '=', self.establishment_id)])
            if customer:
                self.write({
                    'customer_id': customer
                })
            else:
                raise ValidationError('customer not fount')

    @api.model_create_multi
    def create(self, vals_list):
        """Sequence_id"""
        for vals in vals_list:
            if vals.get('order', _('New')) == _('New'):
                vals['order'] = self.env['ir.sequence'].next_by_code(
                    'recurring.subscription') or _('New')
        return super(RecurringSubscription, self).create(vals_list)

    def action_confirm(self):
        """add  button and changing 'state' while clicking it"""
        self.write({
            'state': "confirm"
        })

    def action_cancel(self):
        self.write({
            'state': "cancel"
        })

    def action_auto_invoice(self):
        """Creating Automatic Invoice"""
        today = fields.Date.today()
        subscription_id = self.env['recurring.subscription'].search([('due_date', '<', today)])
        for rec in subscription_id:
            confirm_state = rec.recurring_credit_ids.filtered(
                lambda line: line.state == 'confirm')
            for record in confirm_state:
                self.env['account.move'].create([
                    {
                        'move_type': 'out_invoice',
                        'invoice_date': today,
                        'partner_id': record.partner_id.id,
                        'currency_id': 1,
                        'invoice_line_ids': [
                            Command.create({
                                'product_id': rec.product_id.id,
                                'name': rec.name,
                                'quantity': 1,
                                'price_unit': record.credit_amount,
                            }),
                        ],
                    },
                ])

    def action_email(self):
        """sending mail while state is in 'confirm' """
        if self.state == 'confirm':
            template = self.env.ref('subscription.recurring_subscription_email')
            template.send_mail(self.id, force_send=True)
