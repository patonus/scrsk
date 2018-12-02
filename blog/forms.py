from django import forms

class SearchOptionsForm(forms.Form):
    ascending_order = forms.ChoiceField(label='Sortuj od', choices = (('false', 'Najnowszych'), ('true', 'Najstarszych')))
    search_pattern = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Szukaj'}), required=False)
    search_title = forms.BooleanField(required=False)
    search_author = forms.BooleanField(required=False)
