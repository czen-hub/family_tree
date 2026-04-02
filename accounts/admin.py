from django.contrib import admin
from .models import FamilyMember

@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = [
        'first_name',
        'middle_name',
        'last_name',
        'gender',
        'marital_status',
        'father',
        'mother',
        'spouse',
        'date_of_birth',
        'address',
    ]
    search_fields = ['first_name', 'last_name']
    list_filter = ['marital_status', 'gender', 'last_name']