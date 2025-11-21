from django import forms
from .models import Crop, CustomUser, AbonoApplication

class AbonoApplicationForm(forms.ModelForm):
    class Meta:
        model = AbonoApplication
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows":2, "placeholder":"Notas sobre la aplicación de abono (opcional)"})
        }


class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ["name", "description", "sowing_date", "latitude", "longitude"]
        widgets = {
            "sowing_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3, "cols": 50}),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["display_name", "profile_photo", "bio"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
