import logging
logger = logging.getLogger(__name__)

from unittest import TestCase

from adyen.interface import PaymentInterface


class SessionTest(TestCase):
    """ Test initiating payments. """

    # Source: documentation
    secret = 'Kah942*$7sdp0)'
    session_data = \
        {'merchantReference': 'Internet Order 12345',
         'paymentAmount': '10000',
         'currencyCode': 'GBP',
         'shipBeforeDate': '2007-10-20',
         'skinCode': '4aD37dJA',
         'merchantAccount': 'TestMerchant',
         'shopperLocale': 'en_GB',
         'orderData': 'H4sIAAAAAAAAALMpsOPlCkssyswvLVZIz89PKVZIzEtRKE4tKstMTi3W4+Wy0S+wAwDOGUCXJgAAAA==',
         'sessionValidity': '2007-10-11T11:00:00Z',
         'merchantSig': '33syARtfsxD47jeXzOlEyZ0j3pg='}
    result_data = \
        {'authResult': 'AUTHORISED',
         'pspReference': '1211992213193029',
         'merchantReference': 'Internet Order 12345',
         'skinCode': '4aD37dJA',
         'paymentMethod': 'banktransfer_nl',
         'shopperLocale': 'en_GB',
         'merchantSig': 'ytt3QxWoEhAskUzUne0P5VA9lPw='}

    def test_signature(self):
        """ Test the signature against documentation examples. """
        interface = PaymentInterface(self.secret, self.session_data)
        interface.sign()

        self.assertIn('merchantSig', interface.data)

        signature = interface.data['merchantSig']
        self.assertEquals(signature, 'x58ZcRVL1H6y+XSeBGrySJ9ACVo=')

    def test_validation(self):
        """ Create a signature and check whether validation succeeds. """
        interface = PaymentInterface(self.secret, self.result_data)

        plaintext = interface._data_to_plaintext(interface.RESULT_SIGNATURE_FIELDS)
        signature = interface._sign_plaintext(plaintext)

        self.assertEqual(signature, 'ytt3QxWoEhAskUzUne0P5VA9lPw=')

        self.assertTrue(interface.validate())

    def test_validation_fails(self):
        """ See whether we fail when we have a mismatching signature. """
        false_data = self.result_data.copy()
        false_data['merchantReference'] = 'blabla'

        interface = PaymentInterface(self.secret, false_data)

        self.assertFalse(interface.validate())

    def test_validation_unicode(self):
        """
        Make sure validation still works if we pass along weird unicode
        characters.
        """
        weird_string = u'Was\x9f'

        difficult_data = self.session_data.copy()
        difficult_data['merchantReference'] = weird_string

        interface = PaymentInterface(self.secret, difficult_data)

        interface.sign()

        # TODO: Check whether the signature matches the result in the
        # testing situation

