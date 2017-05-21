from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_id = 'contactForm'
    helper.form_class = 'GeneralForm shake'
    helper.form_action = 'contact'
    helper.form_show_labels = False

    helper.layout = Layout(
        Field('name', 
            placeholder='Name'),
        Field('email',
            placeholder='Email'),
        Field('subject',
            placeholder='Subject'),
        Field('message',
            placeholder='Message'),

        Submit('submit', 'Submit', css_class='btn-system btn-large')
    )