from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

class EditProfileForm(forms.Form):
    #home_town = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_id = 'editProfileForm'
    helper.form_class = 'GeneralForm shake'
    helper.form_action = 'edit_profile'
    helper.form_show_labels = False

    helper.layout = Layout(
        #Field('home_town', 
        #    placeholder='Home Town'),
        Field('first_name',
            placeholder='First Name'),
        Field('last_name',
            placeholder='Last Name'),

        Submit('submit', 'Submit', css_class='btn-system btn-large')
    )