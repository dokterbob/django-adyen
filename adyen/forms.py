from django import forms

from adyen.interface import PaymentInterface
from adyen import settings


class HiddinInputForm(forms.Form):
    """ Form which by default renders all initial_data as hidden fields. """

    def __init__(self, initial_data, *args, **kwargs):
        super(HiddinInputForm, self).__init__(*args, **kwargs)

        for name, value in initial_data.items():
            self.fields[name] = forms.CharField(widget=forms.HiddenInput,
                initial=value)


class AdyenForm(HiddinInputForm):
    """
    Subclass of the HiddenInputForm, making sure stuff like signatures are
    set properly after initialization of the variables and also setting
    some fields from Django settings.
    """

    def __init__(self, initial_data, *args, **kwargs):
        # Set some defaults from the settings
        new_data = {'skinCode': settings.DEFAULT_SKIN,
                    'merchantAccount': settings.MERCHANT_ACCOUNT}

        # Always allow for overriding of the defaults with custom data
        new_data.update(initial_data)

        # Create an interface and sign the data - this updates the data
        # in-place
        self.interface = PaymentInterface(secret=settings.MERCHANT_SECRET,
                                          data=new_data,
                                          testing=settings.DEBUG,
                                          onepage=settings.ONE_PAGE)
        self.interface.sign()

        super(AdyenForm, self).__init__(new_data, *args, **kwargs)


