from django import forms
from django.contrib.auth.models import Group,User
from django.contrib.auth.forms import UserCreationForm
from django.forms import widgets

class DateForm(forms.Form):
     tanggal = forms.DateField(input_formats = ['%m/%d/%Y'])

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

        widgets = {
            'username' : forms.TextInput(
                attrs= {
                    'class':'input100',
                    'placeholder':'Username',
                }
            ),

            'email' : forms.EmailInput(
                attrs= {
                    'class':'input100',
                    'placeholder':'Email',
                }
            ),
            
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].widget = widgets.PasswordInput(
            attrs={
                'placeholder': 'Password',
                'class': 'input100'
            })
        self.fields['password2'].widget = widgets.PasswordInput(
            attrs={
                'placeholder': 'Ulangi Password',
                'class': 'input100'
            }) 
