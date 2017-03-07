
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

from .models import Videos

class SubmitVideoForm(forms.Form):
    category = forms.CharField(max_length=50)
    url = forms.CharField(max_length=200)
    
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_id = 'submitVideoForm'
    helper.form_class = 'GeneralForm shake'
    helper.form_action = 'submit_video'
    helper.form_show_labels = False

    helper.layout = Layout(
        Field('category', 
            placeholder='Category'),
        Field('url',
            placeholder='URL'),
        
        Submit('submit', 'Submit', css_class='btn-system btn-large')
    )