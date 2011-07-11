import logging
logger = logging.getLogger(__name__)

from adyen import settings
from adyen.interface import PaymentInterface


def get_payment_interface(data):
    """ Instantiate a new payment interface with given data. """
    return PaymentInterface(secret=settings.MERCHANT_SECRET,
                            data=data,
                            testing=settings.DEBUG,
                            onepage=settings.ONE_PAGE)

