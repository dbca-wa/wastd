from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from django import forms


class TurtleSearchForm(forms.Form):
    turtle_id = forms.IntegerField(label=False, required=False)
    tag_id = forms.CharField(label=False, max_length=64, required=False)
    pit_tag_id = forms.CharField(label=False, max_length=64, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Field('turtle_id', placeholder='Turtle ID'),
            Field('tag_id', placeholder='Tag ID'),
            Field('pit_tag_id', placeholder='Pit tag ID'),
            Submit('search', 'Search', css_class='btn'),
        )