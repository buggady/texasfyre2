from django import forms

class EditProfileForm(forms.Form):
    home_town = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)