from django.db import models
from django.contrib.auth.models import User
from datetime import date

MARITAL_STATUS = [
    ('Single', 'Single'),
    ('Married', 'Married'),
]

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

# Tibetan calendar animals — cycle of 12 starting from 1900 (Dragon year)
TIBETAN_ANIMALS = [
    'Iron Rat', 'Iron Ox', 'Iron Tiger', 'Iron Rabbit',   # placeholder, real calc below
]

TIBETAN_ANIMAL_CYCLE = [
    'Rat', 'Ox', 'Tiger', 'Rabbit', 'Dragon', 'Snake',
    'Horse', 'Sheep', 'Monkey', 'Rooster', 'Dog', 'Pig',
]

TIBETAN_ELEMENT_CYCLE = [
    'Iron', 'Iron', 'Water', 'Water', 'Wood', 'Wood',
    'Fire', 'Fire', 'Earth', 'Earth', 'Iron', 'Iron',
]

def get_tibetan_year(year):
    """Return Tibetan element-animal for a given Gregorian year."""
    if not year:
        return ''
    # Tibetan year offset: 1900 = Iron Rat
    offset = (year - 1900) % 60
    animal_index  = offset % 12
    element_index = offset % 10
    elements = ['Iron','Iron','Water','Water','Wood','Wood','Fire','Fire','Earth','Earth']
    animals  = ['Rat','Ox','Tiger','Rabbit','Dragon','Snake','Horse','Sheep','Monkey','Rooster','Dog','Pig']
    return f"{elements[element_index]} {animals[animal_index]}"


class FamilyMember(models.Model):
    user           = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name     = models.CharField(max_length=100)
    middle_name    = models.CharField(max_length=100, blank=True)
    last_name      = models.CharField(max_length=100)
    gender         = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS, default='Single')
    date_of_birth  = models.DateField(null=True, blank=True)
    date_of_death  = models.DateField(null=True, blank=True)   # ← new
    address        = models.TextField(blank=True)
    photo          = models.ImageField(upload_to='members/', blank=True, null=True)

    # Contact & social
    phone          = models.CharField(max_length=30, blank=True)
    facebook       = models.CharField(max_length=200, blank=True)
    instagram      = models.CharField(max_length=200, blank=True)

    father = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children_of_father'
    )
    mother = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children_of_mother'
    )
    spouse = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='married_to'
    )

    @property
    def is_deceased(self):
        return self.date_of_death is not None

    @property
    def tibetan_year(self):
        if self.date_of_birth:
            return get_tibetan_year(self.date_of_birth.year)
        return ''

    def get_children(self):
        from itertools import chain
        children = list(chain(
            self.children_of_father.all(),
            self.children_of_mother.all()
        ))
        # Remove duplicates (child may appear via both father and mother link)
        seen = set()
        unique = []
        for c in children:
            if c.pk not in seen:
                seen.add(c.pk)
                unique.append(c)
    # Sort oldest (earliest dob) to youngest — None dates go to the right
        return sorted(unique, key=lambda c: c.date_of_birth or date.max)

    def __str__(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name[0]}."
        return f"{self.first_name} {self.last_name[0]}."