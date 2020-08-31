"""Form for the elternbrief application"""

from django import forms


class UserImportForm(forms.Form):
    """Simple form for uploading csv files for importing users."""
    parents_file = forms.FileField(required=True, widget=forms.FileInput(attrs={'class': 'custom-file-input'}))
    students_file = forms.FileField(required=True, widget=forms.FileInput(attrs={'class': 'custom-file-input'}))
