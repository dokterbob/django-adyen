import logging
logger = logging.getLogger(__name__)

import base64
import hmac
from hashlib import sha1


class PaymentInterface(object):
    """
    Wrapper around Adyen API calls.

    This object is stateless and can be used independently from Django.
    """

    # URL's for single- and multi-page checkouts (test and production)
    TEST_URL_BASE = 'https://test.adyen.com/hpp/'
    TEST_URL_SINGLE = TEST_URL_BASE + 'pay.shtml'
    TEST_URL_MULTIPLE = TEST_URL_BASE + 'select.shtml'

    PROD_URL_BASE = 'https://live.adyen.com/hpp/'
    PROD_URL_SINGLE = TEST_URL_BASE + 'pay.shtml'
    PROD_URL_MULTIPLE = TEST_URL_BASE + 'select.shtml'

    # Fields used for signing payment requests
    SESSION_SIGNATURE_FIELDS = \
        ('paymentAmount', 'currencyCode', 'shipBeforeDate',
         'merchantReference', 'skinCode', 'merchantAccount',
         'sessionValidity', 'shopperEmail', 'shopperReference',
         'allowedMethods', 'blockedMethods', 'shopperStatement',
         'billingAddressType')

    # Fields used for signing billing addresses
    ADDRESS_SIGNATURE_FIELDS = \
        ('billingAddress.street', 'billingAddress.houseNumberOrName',
         'billingAddress.city', 'billingAddress.postalCode',
         'billingAddress.stateOrProvince', 'billingAddress.country')

    # Fields used for verification of result signatures
    RESULT_SIGNATURE_FIELDS = \
        ('authResult', 'pspReference', 'merchantReference', 'skinCode')

    # Required fields for setting up a payment session, except `merchantSig`
    SESSION_REQUIRED_FIELDS = frozenset(
        ('merchantReference', 'paymentAmount', 'currencyCode',
         'shipBeforeDate', 'skinCode', 'merchantAccount', 'sessionValidity'))

    def __init__(self, secret, data):
        self.secret = secret
        self.data = data

    def _sign_plaintext(self, plaintext):
        """
        Sign the string `plaintext` with the shared secret using HMAC and
        encode the result as a base64 encoded string.

        Source: Adyen Python signature implementation example.
        """

        hm = hmac.new(self.secret, plaintext, sha1)
        return base64.encodestring(hm.digest()).strip()

    def _data_to_plaintext(self, fields):
        """
        Concatenate the specified `fields` from the `data` dictionary.
        """
        plaintext = ''
        for field in fields:
            plaintext += self.data.get(field, '')

        return plaintext

    def sign(self):
        """ Sign data. """

        data_fields = self.data.keys()

        # Make sure all required fields are filled in
        assert self.SESSION_REQUIRED_FIELDS.issubset(data_fields), \
            'Not all required fields are set.'

        plaintext = self._data_to_plaintext(self.SESSION_SIGNATURE_FIELDS)

        # Set the merchant signature in data
        self.data['merchantSig'] = self._sign_plaintext(plaintext)

        # See whether one of the billing address fields are set
        # If so, calculate the billing address signature.
        for address_field in self.ADDRESS_SIGNATURE_FIELDS:
            if address_field in data_fields:
                billing_plaintext = \
                    self._data_to_plaintext(self.ADDRESS_SIGNATURE_FIELDS)
                self.data['billingAddressSig'] = \
                    self._sign_plaintext(billing_plaintext)

                # No need to continue, we already calculated the signature
                # for all billing fields
                break
