from django.db import models
from django.contrib.auth.models import User

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