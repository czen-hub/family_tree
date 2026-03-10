from django.contrib import admin
from .models import FamilyMember

@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'middle_name', 'last_name', 'date_of_birth', 'address', 'father_name', 'mother_name', 'grandfather_name', 'grandmother_name']