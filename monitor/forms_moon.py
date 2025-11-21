from django import forms

class MoonCalendarForm(forms.Form):
    date = forms.DateField(label="Fecha de consulta", widget=forms.DateInput(attrs={"type": "date"}))
