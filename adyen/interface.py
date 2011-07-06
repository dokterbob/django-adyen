import logging
logger = logging.getLogger(__name__)

from adyen import settings


class PaymentInterface(object):
    """
    Wrapper around Adyen API calls.

    This object is stateless and does not use any settings, hence it can be
    used easily in non-Django applications.
    """

    # URL's for single- and multi-page checkouts (test and production)
    TEST_URL_BASE = 'https://test.adyen.com/hpp/'
    TEST_URL_SINGLE = TEST_URL_BASE + 'pay.shtml'
    TEST_URL_MULTIPLE = TEST_URL_BASE + 'select.shtml'

    PROD_URL_BASE = 'https://live.adyen.com/hpp/'
    PROD_URL_SINGLE = TEST_URL_BASE + 'pay.shtml'
    PROD_URL_MULTIPLE = TEST_URL_BASE + 'select.shtml'

    # Fields used for signing payment requests
    REQUEST_SIGNATURE_FIELDS = \
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

    def __init__(self, params=None, request=None):
        """
        Initialize the interface.
        """
        assert request or params, \
            'Please specify either a request or a set of parameters'

        if not params:
            params = request.REQUEST

        self.params = params

        # We haven't parsed anything yet
        self.parsed = False

    @staticmethod
    def _sign_plaintext(plaintext, secret):
        """
        Sign the string `plaintext` with a given `secret` using HMAC and
        encode the result as a base64 encoded string.

        Source: Adyen Python signature implementation example.
        """
        import base64
        import hmac
        import hashlib

        hm = hmac.new(secret, data, hashlib.sha1)
        return base64.encodestring(hm.digest()).strip()

    @staticmethod
    def _data_to_plaintext(data, fields):
        """
        Concatenate the specified `fields` from the `data` dictionary.
        """
        plaintext = ''
        for field in fields:
            plaintext += data.get(field, '')

        return plaintext
