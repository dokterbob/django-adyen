from django import forms

class HiddinInputForm(forms.Form):
    """ Form which by default renders all initial_data as hidden fields. """

    def __init__(self, initial_data, *args, **kwargs):
        super(HiddinInputForm, self).__init__(*args, **kwargs)

        for name, value in initial_data.items():
            self.fields[name] = forms.CharField(widget=forms.HiddenInput,
                initial=value)