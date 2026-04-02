from django import forms
from .models import FamilyMember

LAST_NAME_CHOICES = [
    ('', '-- Select Last Name --'),
    ('Chyaba', 'Chyaba'),
    ('Shangba', 'Shangba'),
    ('Dongba', 'Dongba'),
    ('Yeba', 'Yeba'),
]

COUNTRY_CHOICES = [
    ('', '-- Select Country --'),
    ('Nepal', 'Nepal'),
    ('India', 'India'),
    ('UAE', 'UAE'),
    ('Portugal', 'Portugal'),
    ('USA', 'USA'),
    ('South Korea', 'South Korea'),
    ('Australia', 'Australia'),
    ('Canada', 'Canada'),
    ('Japan', 'Japan'),
    ('Qatar', 'Qatar'),
]

MARITAL_STATUS_CHOICES = [
    ('', '-- Select Status --'),
    ('Single', 'Single'),
    ('Married', 'Married'),
]

GENDER_CHOICES = [
    ('', '-- Select Gender --'),
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

class FamilyMemberForm(forms.ModelForm):
    last_name = forms.ChoiceField(choices=LAST_NAME_CHOICES, widget=forms.Select)
    marital_status = forms.ChoiceField(choices=MARITAL_STATUS_CHOICES, widget=forms.Select)
    address = forms.ChoiceField(choices=COUNTRY_CHOICES, widget=forms.Select)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select)

    class Meta:
        model = FamilyMember
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'gender',
            'marital_status',
            'date_of_birth',
            'address',
            'father',
            'mother',
            'spouse',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'father': forms.Select,
            'mother': forms.Select,
            'spouse': forms.Select,
        }