from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

class DonatePhotosForm(forms.Form):
    facebook_album_id = forms.IntegerField()
    #zip_folder = forms.FileField()
    #images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_id = 'DonatePhotosForm'
    helper.form_class = 'GeneralForm shake'
    helper.form_action = 'donate_photos'
    helper.form_show_labels = False

    helper.layout = Layout(
        Field('facebook_album_id', 
            placeholder='Event Album ID'),
        #Field('zip_folder',
        #    placeholder='Zip Folder'),
        #Field('images',
        #    placeholder='Images'),

        Submit('submit', 'Submit', css_class='btn-system btn-large')
    )

class SubmitEventIdeaForm(forms.Form):
    title = forms.CharField()
    location = forms.CharField()

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_id = 'SubmitEventIdeaForm'
    helper.form_class = 'GeneralForm shake'
    helper.form_action = 'submit_event_idea'
    helper.form_show_labels = False

    helper.layout = Layout(
        Field('title', 
            placeholder='Name of Event'),
        Field('location',
            placeholder='Location of Event'),

        Submit('submit', 'Submit', css_class='btn-system btn-large')
    )

class SubmitPastEventForm(forms.Form):
    title = forms.CharField()
    location = forms.CharField()

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_id = 'SubmitPastEventForm'
    helper.form_class = 'GeneralForm shake'
    helper.form_action = 'submit_past_event'
    helper.form_show_labels = False

    helper.layout = Layout(
        Field('title', 
            placeholder='Name of Event'),
        Field('location',
            placeholder='Location of Event'),

        Submit('submit', 'Submit', css_class='btn-system btn-large')
    )