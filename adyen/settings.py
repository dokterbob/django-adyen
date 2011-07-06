import logging
logger = logging.getLogger(__name__)

from django.conf import settings


MERCHANT_ACCOUNT = getattr(settings, 'ADYEN_MERCHANT_ACCOUNT')
MERCHANT_SECRET = getattr(settings, 'ADYEN_MERCHANT_SECRET')

DEBUG = getattr(settings, 'ADYEN_DEBUG', True)