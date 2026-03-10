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
    ('South Korea', 'South Korea'),
    ('Qatar', 'Qatar'),
    ('UAE', 'UAE'),
]

GRANDFATHER_CHOICES = [
    ('', '-- Select Grandfather --'),
    ('Karsang Dawa', 'Karsang Dawa'),
    ('Dindu Lama Chyaba', 'Dindu Lama Chyaba'),
    ('Pemba Lama', 'Pemba Lama'),
    ('Temba Lama', 'Temba Lama'),
    ('Mike Sherpa', 'Mike Sherpa'),
    ('AAA Sherpa', 'AAA Sherpa'),
    ('ZZZ', 'ZZZ')
]

GRANDMOTHER_CHOICES = [
    ('', '-- Select Grandmother --'),
    ('xyz', 'xyz'),
    ('Kami Dolma Shangba', 'Kami Dolma Shangba'),
    ('QQQ Lhamu', 'QQQ Lhamu'),
    ('Maya Lhamu', 'Maya Lhamu'),
    ('Tena Sherpa', 'Tena Sherpa'),
    ('BBB Sherpa', 'BBB Sherpa'),
    ('YYY Sherpa', 'YYY Sherpa')

]

MARITAL_STATUS_CHOICES = [
    ('', '-- Select Status --'),
    ('Single', 'Single'),
    ('Married', 'Married'),
]

class FamilyMemberForm(forms.ModelForm):
    last_name = forms.ChoiceField(choices=LAST_NAME_CHOICES, widget=forms.Select)
    marital_status = forms.ChoiceField(choices=MARITAL_STATUS_CHOICES, widget=forms.Select)
    address = forms.ChoiceField(choices=COUNTRY_CHOICES, widget=forms.Select)
    grandfather_name = forms.ChoiceField(choices=GRANDFATHER_CHOICES, widget=forms.Select)
    grandmother_name = forms.ChoiceField(choices=GRANDMOTHER_CHOICES, widget=forms.Select)

    class Meta:
        model = FamilyMember
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'marital_status',
            'spouse_name',
            'date_of_birth',
            'address',
            'father_name',
            'mother_name',
            'grandfather_name',
            'grandmother_name',
        ]