# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hashlib

from odoo import fields, models

# from odoo.addons.payment_payulatam.const import DEFAULT_PAYMENT_METHODS_CODES


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('payu', "PayU")], ondelete={'payu': 'set default'})
    payu_merchant_code = fields.Char(
        string="Merchant ID", help="The ID solely used to identify the account with PayU",
        required_if_provider='payu')
    payu_merchant_key = fields.Char(
        string="Merchant Key", required_if_provider='payu', groups='base.group_system')

