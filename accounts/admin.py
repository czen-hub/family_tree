from django.contrib import admin
from .models import FamilyMember, FamilyGroup, FamilyMembership, UserProfile, Invite, EditHistory


@admin.register(FamilyGroup)
class FamilyGroupAdmin(admin.ModelAdmin):
    list_display  = ['name', 'created_by', 'created_at', 'is_public']
    search_fields = ['name']


@admin.register(FamilyMembership)
class FamilyMembershipAdmin(admin.ModelAdmin):
    list_display  = ['user', 'family_group', 'role']
    list_filter   = ['role', 'family_group']
    search_fields = ['user__username', 'family_group__name']


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display  = [
        'first_name',
        'middle_name',
        'last_name',
        'family_group',
        'gender',
        'marital_status',
        'father',
        'mother',
        'spouse',
        'date_of_birth',
        'address',
    ]
    search_fields = ['first_name', 'last_name']
    list_filter   = ['family_group', 'marital_status', 'gender', 'last_name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'family_group', 'tree_public']
    list_filter  = ['family_group', 'tree_public']


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ['email', 'invited_by', 'family_group', 'role', 'accepted', 'created_at']
    list_filter  = ['accepted', 'family_group', 'role']
    search_fields = ['email', 'invited_by__username']


@admin.register(EditHistory)
class EditHistoryAdmin(admin.ModelAdmin):
    list_display  = ['member_name', 'action', 'changed_by', 'family_group', 'changed_at']
    list_filter   = ['action', 'family_group']
    search_fields = ['member_name', 'changed_by__username']