from django import forms

from .models import Pledge


class PledgeForm(forms.ModelForm):
    class Meta:
        model = Pledge
        fields = ["quantity"]
        labels = {
            "quantity": "Quantidade",
        }
        widgets = {
            "quantity": forms.NumberInput(attrs={"class": "inp", "min": 1}),
        }
