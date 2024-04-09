from django import forms
from django.contrib.auth.models import User
from django.db import models 
from users.models import Profile



class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        try:
            self.user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(f'С таким именим, {username}, пользователя не существует!')

        if not self.user.check_password(password):
            raise forms.ValidationError(f'Пароль для пользователя, {username} некорректный!')


class RegisterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-input'

    class Meta:
        model = User
        fields = ('username', 'password', 'email',)
        widgets = {
            'password': forms.PasswordInput()
        }



class ProfileUser(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-input'
    class Meta:
         model = Profile
         fields = ('phone','addres',)
         widgets = {
            'phone': forms.NumberInput()

         }