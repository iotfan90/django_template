from django import forms
from crispy_forms.helper import FormHelper


class UserLoginForm(forms.Form):
    email = forms.CharField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Email',
                'required': 'required'
            }
        )
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Password',
                'required': 'required'
            }
        ),
        strip=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
