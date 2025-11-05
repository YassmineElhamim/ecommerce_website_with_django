from django.contrib.auth.models import User
from store.models import Order, ShippingAddress
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

class CheckoutForm(forms.ModelForm):
    """Form for checkout - collecting shipping and payment info"""
    
    # Additional fields not in the model
    save_address = forms.BooleanField(
        required=False,
        initial=False,
        label='Save this address for future orders'
    )
    
    class Meta:
        model = Order
        fields = [
            'full_name',
            'email', 
            'phone',
            'address_line1',
            'address_line2',
            'city',
            'postal_code',
            'country',
            'payment_method',
            'notes'
        ]
        
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
                'placeholder': 'John Doe'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
                'placeholder': 'name@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
                'placeholder': '+212 6XX XXX XXX'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
                'placeholder': 'Street address, apartment, suite, etc.'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
                'placeholder': 'Additional address info (optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
                'placeholder': 'Casablanca'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
                'placeholder': '20000'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
                'placeholder': 'Morocco'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
                'placeholder': 'Additional notes about your order (optional)',
                'rows': 3
            }),
        }
        
        labels = {
            'full_name': 'Full Name',
            'address_line1': 'Address',
            'address_line2': 'Address Line 2',
            'postal_code': 'Postal Code',
            'payment_method': 'Payment Method',
            'notes': 'Order Notes'
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Add phone validation if needed
        if phone and len(phone) < 10:
            raise forms.ValidationError('Please enter a valid phone number')
        return phone
    
    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        # Add postal code validation if needed
        return postal_code


class GuestCheckoutForm(forms.Form):
    """Simplified form for guest checkout"""
    
    # Contact Info
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
            'placeholder': 'name@example.com'
        })
    )
    
    # Shipping Info
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
            'placeholder': 'John Doe'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
            'placeholder': '+212 6XX XXX XXX'
        })
    )
    
    address_line1 = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
            'placeholder': 'Street address'
        })
    )
    
    address_line2 = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
            'placeholder': 'Apartment, suite, etc. (optional)'
        })
    )
    
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
            'placeholder': 'Casablanca'
        })
    )
    
    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
            'placeholder': '20000'
        })
    )
    
    country = forms.CharField(
        max_length=100,
        initial='Morocco',
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
            'placeholder': 'Morocco'
        })
    )
    
    # Payment
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-yellow-500 focus:ring-yellow-500',
            'placeholder': 'Additional notes (optional)',
            'rows': 3
        })
    )   