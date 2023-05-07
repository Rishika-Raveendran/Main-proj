from django import forms
from .models import *

class CsvFileForm(forms.ModelForm):
    class Meta:
        model = CSVModel
        fields = ('branch','csv_file')