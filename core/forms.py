from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm

from .models import User


class StyledFormMixin:
    """Aplica a classe .inp do design system em todos os widgets do formulário."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "inp")


class LoginForm(StyledFormMixin, AuthenticationForm):
    pass


class RegisterForm(StyledFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ["name", "email"]


class NameForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["name"]


class PasswordForm(StyledFormMixin, PasswordChangeForm):
    pass
