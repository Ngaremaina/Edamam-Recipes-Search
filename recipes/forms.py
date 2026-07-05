from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User


class TailwindStyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})


class RegisterForm(TailwindStyledFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')


class StyledAuthenticationForm(TailwindStyledFormMixin, AuthenticationForm):
    pass


class StyledPasswordResetForm(TailwindStyledFormMixin, PasswordResetForm):
    pass


class StyledSetPasswordForm(TailwindStyledFormMixin, SetPasswordForm):
    pass
