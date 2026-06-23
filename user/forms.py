from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

PERMISSION_CHOICES = (
    ('normal', '一般使用者'),
    ('staff', '員工'),
    ('superuser', '管理員'),
)


class UserRegistrationForm(UserCreationForm):
    """公開註冊表單 - 新使用者無法選擇權限，預設為一般使用者"""
    first_name = forms.CharField(label='使用者姓名', max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = '帳號'
        self.fields['password1'].label = '密碼'
        self.fields['password2'].label = '確認密碼'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        # 新使用者預設為一般使用者，無法更改
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label='使用者姓名', max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)
    permission_type = forms.ChoiceField(label='權限類別', choices=PERMISSION_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'permission_type', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = '帳號'
        self.fields['password1'].label = '密碼'
        self.fields['password2'].label = '確認密碼'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        permission_type = self.cleaned_data['permission_type']
        user.is_staff = permission_type in ['staff', 'superuser']
        user.is_superuser = permission_type == 'superuser'
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    first_name = forms.CharField(label='使用者姓名', max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)
    permission_type = forms.ChoiceField(label='權限類別', choices=PERMISSION_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'permission_type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = '帳號'
        self.fields['username'].disabled = True
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.first_name
            self.fields['email'].initial = self.instance.email
            if self.instance.is_superuser:
                self.fields['permission_type'].initial = 'superuser'
            elif self.instance.is_staff:
                self.fields['permission_type'].initial = 'staff'
            else:
                self.fields['permission_type'].initial = 'normal'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        permission_type = self.cleaned_data['permission_type']
        user.is_staff = permission_type in ['staff', 'superuser']
        user.is_superuser = permission_type == 'superuser'
        if commit:
            user.save()
        return user


class UserSelfEditForm(forms.ModelForm):
    first_name = forms.CharField(label='使用者姓名', max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = '帳號'
        self.fields['username'].disabled = True
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.first_name
            self.fields['email'].initial = self.instance.email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
