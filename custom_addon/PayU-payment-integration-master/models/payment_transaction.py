import urllib
from odoo import models, _
from odoo.addons.payment import utils as payment_utils
import hashlib
import requests

from odoo.exceptions import ValidationError


class PaymentTransaction(models.Model):
    """Inheriting model payment transaction"""
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Payu-specific rendering values.
        Note: self.ensure_one() from `_get_processing_values`
        :param dict processing_values: The generic and specific processing
        values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """

        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'payu':
            return res

        api_key = self.provider_id.payu_merchant_code
        txn_id = self.reference
        amount = int(self.amount)
        print(type(amount),'ufed')
        product_info = self.reference
        first_name, last_name = payment_utils.split_partner_name(
            self.partner_id.name)
        email = self.partner_email
        salt = self.provider_id.payu_merchant_key
        surl = "https://de34-111-92-105-22.ngrok-free.app/payment/payu/return"
        furl = "https://de34-111-92-105-22.ngrok-free.app/payment/payu/return"
        hash_string = f"{api_key}|{txn_id}|{amount}|{product_info}|{first_name}|{email}|||||||||||{salt}"
        hash = hashlib.sha512(hash_string.encode()).hexdigest()
        print('hash', hash)

        api_url = 'https://test.payu.in/_payment'
        payload = {
            'key': api_key,
            'txnid': txn_id,
            'amount': amount,
            'productinfo': product_info,
            'firstname': first_name,
            'email': email,
            'phone': self.partner_phone,
            'surl': surl,
            'furl': furl,
            'hash': hash,
        }
        # Encode the parameters for use in the URL
        encodedParams = urllib.parse.urlencode(payload)

        # Build the URL for the PayU API request
        # url = api_url + "?" + encodedParams
        # print('url', url)
        print('payu values with hash', encodedParams)
        print('payu values with hash', payload)
        headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
        response = requests.request("POST", api_url, data=encodedParams, headers=headers)
        return payload

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on Payu data. """


        tx_value = super()._get_tx_from_notification_data(provider_code,
                                                          notification_data)
        print("thummmm", tx_value)
        # print(notification_data, "jjjjjjj")
        # if provider_code != 'payu' or len(tx_value) == 1:
        #     return tx_value
        # reference = notification_data.get('txnid')
        # if not reference:
        #     raise ValidationError(
        #         "PayU: " + _("Received data with missing reference (%s)",
        #                      reference)
        #     )
        # tx_value = self.sudo().search([('reference', '=', reference),
        #                                ('provider_code', '=', 'payu')])
        # if not tx_value:
        #     raise ValidationError(
        #         "PayU: " + _("No transaction found matching reference %s.",
        #                      reference)
        #     )
        # return tx_value
