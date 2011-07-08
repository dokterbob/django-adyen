import logging
logger = logging.getLogger(__name__)

from django.test import TestCase


class SessionTest(TestCase):
    """ Test initiating payments. """

    def test_signature(self):
        """ Test the signature against Adyen's online signature tester. """
        pass

    def test_validation(self):
        """ Create a signature and check whether validation succeeds. """
        pass

    def test_session(self):
        """ Test whether initiating a payment session works. """
        pass

    def test_result(self):
        """ Test whether a result call gets processed in the right way. """
        pass