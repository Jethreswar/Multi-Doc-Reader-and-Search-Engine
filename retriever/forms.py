from django import forms
from .models import Documents

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Documents
        fields = ['file']
    
class SearchForm(forms.Form):
    query = forms.CharField(max_length=255)