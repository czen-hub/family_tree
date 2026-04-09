from django.db import models
from django.contrib.auth.models import User
from datetime import date
import uuid

MARITAL_STATUS = [
    ('Single', 'Single'),
    ('Married', 'Married'),
]

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
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
    if not year:
        return ''
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
    date_of_death  = models.DateField(null=True, blank=True)
    address        = models.TextField(blank=True)
    photo          = models.ImageField(upload_to='members/', blank=True, null=True)
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
    def age(self):
        if not self.date_of_birth:
            return None
        end = self.date_of_death or date.today()
        return end.year - self.date_of_birth.year - (
            (end.month, end.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

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
        seen = set()
        unique = []
        for c in children:
            if c.pk not in seen:
                seen.add(c.pk)
                unique.append(c)
        return sorted(unique, key=lambda c: c.date_of_birth or date.max)

    def __str__(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name[0]}."
        return f"{self.first_name} {self.last_name[0]}."


class EditHistory(models.Model):
    ACTION_CHOICES = [
        ('add',    'Added'),
        ('edit',   'Edited'),
        ('delete', 'Deleted'),
    ]
    member      = models.ForeignKey(FamilyMember, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='history')
    member_name = models.CharField(max_length=200)  # store name in case member deleted
    action      = models.CharField(max_length=10, choices=ACTION_CHOICES)
    changed_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at  = models.DateTimeField(auto_now_add=True)
    notes       = models.TextField(blank=True)  # optional summary of what changed

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.changed_by} {self.action} {self.member_name} at {self.changed_at}"


class UserProfile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tree_public = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} profile"


class Invite(models.Model):
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invites_sent')
    email      = models.EmailField()
    token      = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    accepted   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invite to {self.email} from {self.invited_by.username}"