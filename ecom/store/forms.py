from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import *

class SignUpForm(UserCreationForm):
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	phone = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Phone Number'}))
	address = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Address'}))

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'address', 'password1', 'password2')

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'

class CheckoutForm(forms.Form):

	class Meta:
		model = Order
		fields = '__all__'

	first_name = forms.CharField(label='First Name', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
	last_name = forms.CharField(label='Last Name', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
	address_line1 = forms.CharField(label='Address Line 1', max_length=255, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Ex:123 Main St'}))
	address_line2 = forms.CharField(label='Address Line 2', max_length=255, required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Apartment or suite'}))
	city = forms.CharField(label='City', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
	state = forms.CharField(label='State', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
	postal_code = forms.CharField(label='Postal Code', max_length=20, widget=forms.TextInput(attrs={'class':'form-control'}))
	country = forms.CharField(label='Country', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))


    # New payment type field
	payment_type = forms.ChoiceField(label='Payment Type', choices=[
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('other', 'Other'),
    ])
	# Payment-related fields
	name_on_card = forms.CharField(label='Name on Card', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
	card_number = forms.CharField(label='Card Number', max_length=16, widget=forms.TextInput(attrs={'class':'form-control'}))
	expiration_date = forms.DateField(label='Expiration Date', widget=forms.DateInput(attrs={'class':'form-control','placeholder': 'MM/YY'}))
	cvv = forms.CharField(label='CVV', max_length=4, widget=forms.TextInput(attrs={'class':'form-control'}))
