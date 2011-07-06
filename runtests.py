#!/usr/bin/env python
import sys, logging
from os.path import dirname, abspath
from django.conf import settings

logging.basicConfig(level=logging.DEBUG)

try:
    from test_secrets import MERCHANT_NAME, MERCHANT_PASSWORD
except ImportError:
    sys.exit('Must define MERCHANT_NAME and MERCHANT_PASSWORD in test_secrets.py first!')

if not settings.configured:
    settings.configure(
        ADYEN_MERCHANT_NAME=MERCHANT_NAME,
        ADYEN_MERCHANT_PASSWORD=MERCHANT_PASSWORD,
        DATABASE_ENGINE='sqlite3',
        # HACK: this fixes our threaded runserver remote tests
        DATABASE_NAME='test_ADYEN.sqlite',
        TEST_DATABASE_NAME='test_adyen.sqlite',
        INSTALLED_APPS=[
            'adyen',
        ],
        ROOT_URLCONF='adyen.urls',
        DEBUG=False,
        SITE_ID=1,
    )

from django.test.simple import run_tests

def runtests(*test_args):
    if not test_args:
        test_args = ['adyen']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    failures = run_tests(test_args, verbosity=1, interactive=True)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])