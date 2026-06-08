from django import forms

from .models import Pledge


class PledgeForm(forms.ModelForm):
    class Meta:
        model = Pledge
        fields = ["quantity", "person_name"]
        labels = {
            "quantity": "Quantidade",
            "person_name": "Nome",
        }
        widgets = {
            "quantity": forms.NumberInput(attrs={"class": "inp", "min": 1}),
            "person_name": forms.TextInput(attrs={"class": "inp", "data-remember-name": ""}),
        }
