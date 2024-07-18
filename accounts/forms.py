from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import AuthenticationForm


class UserForm(forms.ModelForm):
    # groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple)
    groups = forms.ModelChoiceField(queryset=Group.objects.all(), widget=forms.Select)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'groups']
        widgets = {
            'password': forms.PasswordInput(),
        }

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
