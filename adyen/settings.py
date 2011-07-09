import logging
logger = logging.getLogger(__name__)

from django.conf import settings

# Required settings
MERCHANT_ACCOUNT = getattr(settings, 'ADYEN_MERCHANT_ACCOUNT')
MERCHANT_SECRET = getattr(settings, 'ADYEN_MERCHANT_SECRET')

# Optional settings
DEBUG = getattr(settings, 'ADYEN_DEBUG', True)
DEFAULT_SKIN = getattr(settings, 'ADYEN_DEFAULT_SKIN', None)
ONE_PAGE = getattr(settings, 'ADYEN_ONE_PAGE', True)