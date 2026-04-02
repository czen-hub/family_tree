from django.db import models
from django.contrib.auth.models import User

MARITAL_STATUS = [
    ('Single', 'Single'),
    ('Married', 'Married'),
]

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

class FamilyMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS, default='Single')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    # ✅ Real links to other FamilyMember records
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

    def get_children(self):
        from itertools import chain
        return list(chain(
            self.children_of_father.all(),
            self.children_of_mother.all()
        ))

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



"""

MARITAL_STATUS = [
    ('Single', 'Single'),
    ('Married', 'Married'),
]

class FamilyMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS, default='Single')
    spouse_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField()
    address = models.TextField()
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    grandfather_name = models.CharField(max_length=100)
    grandmother_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}" 
    
    """