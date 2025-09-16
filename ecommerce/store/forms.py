from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border border-gray-300 bg-gray-50 p-2.5 text-gray-900 focus:border-yellow-500 focus:ring-yellow-500 sm:text-sm',
            'placeholder': 'Email Address'
        })
    )


    first_name = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border border-gray-300 bg-gray-50 p-2.5 text-gray-900 focus:border-yellow-500 focus:ring-yellow-500 sm:text-sm',
            'placeholder': 'First Name'
        })
    )


    last_name = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border border-gray-300 bg-gray-50 p-2.5 text-gray-900 focus:border-yellow-500 focus:ring-yellow-500 sm:text-sm',
            'placeholder': 'Last Name'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        tailwind_input_class = 'block w-full rounded-md border border-gray-300 bg-gray-50 p-2.5 text-gray-900 focus:border-yellow-500 focus:ring-yellow-500 sm:text-sm'

        self.fields['username'].widget.attrs.update({
            'class': tailwind_input_class,
            'placeholder': 'Enter your Username'
        })
        self.fields['username'].label = ''
        self.fields['username'].help_text = ''


        self.fields['password1'].widget.attrs.update({
            'class': tailwind_input_class,
            'placeholder': 'Enter password'
        })
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = ''


        self.fields['password2'].widget.attrs.update({
            'class': tailwind_input_class,
            'placeholder': 'Enter confirm password'
        })
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = ''

    