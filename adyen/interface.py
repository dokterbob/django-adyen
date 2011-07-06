import logging
logger = logging.getLogger(__name__)

import base64
import hmac
from hashlib import sha1

from urllib import urlencode


class PaymentInterface(object):
    """
    Wrapper around Adyen API calls.

    This object is stateless and can be used independently from Django.
    """

    # URL's for single- and multi-page checkouts (test and production)
    URL_BASE_TEST = 'https://test.adyen.com/hpp/'
    URL_BASE_LIVE = 'https://live.adyen.com/hpp/'
    URL_SINGLE = 'pay.shtml'
    URL_MULTIPLE = 'select.shtml'

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

    # Required fields for setting up a payment session, except `merchantSig`
    SESSION_REQUIRED_FIELDS = frozenset(
        ('merchantReference', 'paymentAmount', 'currencyCode',
         'shipBeforeDate', 'skinCode', 'merchantAccount', 'sessionValidity'))

    # Fields used for verification of result signatures
    RESULT_SIGNATURE_FIELDS = \
        ('authResult', 'pspReference', 'merchantReference', 'skinCode')

    # Fields expected to be contained in the results
    RESULT_REQUIRED_FIELDS = frozenset(
        ('authResult', 'pspReference', 'merchantReference', 'skinCode',
         'merchantSig', 'paymentMethod', 'shopperLocale'))

    def __init__(self, secret, data, testing=True, onepage=True):
        self.secret = secret
        self.data = data
        self.testing = testing
        self.onepage = onepage

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

    def get_session_url(self):
        if self.testing:
            baseurl = self.URL_BASE_TEST
        else:
            baseurl = self.URL_BASE_LIVE

        if self.onepage:
            return baseurl + self.URL_SINGLE
        else:
            return baseurl + self.URL_MULTIPLE

    def get_redirect_url(self):
        """
        Construct the redirect URL for starting a payment.
        """

        # Make sure a signature is present in the data
        assert self.data.has_key('merchantSig')
        params = urlencode(self.data)

        session_url = self.get_session_url()

        return session_url + '?' + params

    def sign(self):
        """
        Add required signatures to the session data dictionary. The given
        dictionary is updated in-place.
        """

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

    def validate(self):
        """
        Validate the data signature for a payment result. Returns True when
        the signature is valid, False otherwise.
        """

        data_fields = self.data.keys()

        # Make sure all expected fields are in the result
        assert self.RESULT_REQUIRED_FIELDS.issubset(data_fields), \
            'Not all expected fields are present.'

        plaintext = self._data_to_plaintext(self.RESULT_SIGNATURE_FIELDS)
        signature = self._sign_plaintext(plaintext)

        if not signature == self.data['merchantSig']:
            return False

        return True


