from django import forms


class SearchOptionsForm(forms.Form):
    ascending_order = forms.ChoiceField(label='Sortuj od',
                                        choices=(('false', 'Najnowszych'),
                                                 ('true', 'Najstarszych')),
                                        required=False)
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Szukaj po tytule'}), max_length=100,
                            required=False)
    author = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Szukaj po autorze'}), max_length=100,
                             required=False)
