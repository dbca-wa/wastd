from django import forms
from easy_select2 import apply_select2
from django_select2 import forms as s2forms

from .models import TrtPersons,TrtDataEntry,TrtTags


class tagWidget(s2forms.ModelSelect2Widget):
     search_fields = [
         "tag_id__icontains",
     ]
     def get_queryset(self):
        return TrtTags.objects.all() # or filtered queryset 


class TrtDataEntryForm(forms.ModelForm):
    class Meta:
        model = TrtDataEntry
        fields = "__all__"
        widgets = {
            "recapture_left_tag_id":tagWidget,
            "recapture_left_tag_id_2":tagWidget,
            "recapture_right_tag_id":tagWidget,
            "recapture_right_tag_id_2":tagWidget,
        }

# class TrtDataEntryForm(forms.Form):
  
#     tag = forms.ChoiceField(
#         widget=tagWidget(data_view='wamtram2:my-autocomplete')
        
#     )


class DataEntryUserModelForm(forms.ModelForm):
    qs=TrtPersons.objects.all()
    user_entry_id = forms.ModelChoiceField(queryset=qs, widget=apply_select2(forms.Select))

    def clean(self):
        cleaned_data = super().clean()
        ch = cleaned_data.get('user_entry_id')
        try:
            cleaned_data['user_entry_id'] = int(ch.person_id)
        except ValueError:
            raise forms.ValidationError("Choice must be an integer.")

        return cleaned_data


    
class EnterUserModelForm(forms.ModelForm):
    qs=TrtPersons.objects.all()
    entered_person_id = forms.ModelChoiceField(queryset=qs,widget=apply_select2(forms.Select))
   
    def clean(self):
        cleaned_data = super().clean()
        ch = cleaned_data.get('entered_person_id')
        try:
            cleaned_data['entered_person_id'] = int(ch.person_id)
        except ValueError:
            raise forms.ValidationError("Choice must be an integer.")

        return cleaned_data
