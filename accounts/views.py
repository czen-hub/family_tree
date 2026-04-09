from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from .models import FamilyMember, UserProfile, Invite
from .forms import FamilyMemberForm
import os


def home(request):
    return render(request, 'accounts/home.html')


def register(request):
    token = request.GET.get('token')
    invite = None
    if token:
        try:
            invite = Invite.objects.get(token=token, accepted=False)
        except Invite.DoesNotExist:
            pass

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if invite:
                invite.accepted = True
                invite.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form, 'invite': invite})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    members = FamilyMember.objects.filter(user=request.user)
    member_data = []
    for member in members:
        children = member.get_children()
        member_data.append({
            'member': member,
            'children': children,
        })
    return render(request, 'accounts/dashboard.html', {'member_data': member_data})


@login_required
def family_list(request):
    members = FamilyMember.objects.all().order_by('first_name', 'last_name')
    return render(request, 'accounts/family_list.html', {'members': members})


@login_required
def family_detail(request, pk):
    member = get_object_or_404(FamilyMember, pk=pk)
    children = member.get_children()

    siblings = FamilyMember.objects.none()
    if member.father:
        siblings = siblings | FamilyMember.objects.filter(father=member.father).exclude(pk=pk)
    if member.mother:
        siblings = siblings | FamilyMember.objects.filter(mother=member.mother).exclude(pk=pk)
    siblings = siblings.distinct()

    cousins = FamilyMember.objects.none()
    parent_siblings = FamilyMember.objects.none()
    if member.father:
        if member.father.father:
            parent_siblings = parent_siblings | FamilyMember.objects.filter(
                father=member.father.father
            ).exclude(pk=member.father.pk)
        if member.father.mother:
            parent_siblings = parent_siblings | FamilyMember.objects.filter(
                mother=member.father.mother
            ).exclude(pk=member.father.pk)
    if member.mother:
        if member.mother.father:
            parent_siblings = parent_siblings | FamilyMember.objects.filter(
                father=member.mother.father
            ).exclude(pk=member.mother.pk)
        if member.mother.mother:
            parent_siblings = parent_siblings | FamilyMember.objects.filter(
                mother=member.mother.mother
            ).exclude(pk=member.mother.pk)
    parent_siblings = parent_siblings.distinct()
    for aunt_uncle in parent_siblings:
        cousins = cousins | FamilyMember.objects.filter(
            father=aunt_uncle
        ) | FamilyMember.objects.filter(
            mother=aunt_uncle
        )
    cousins = cousins.distinct().exclude(pk=pk)

    nieces_nephews = FamilyMember.objects.none()
    for sibling in siblings:
        nieces_nephews = nieces_nephews | FamilyMember.objects.filter(
            father=sibling
        ) | FamilyMember.objects.filter(
            mother=sibling
        )
    nieces_nephews = nieces_nephews.distinct()

    grandchildren = FamilyMember.objects.none()
    for child in children:
        for grandchild in child.get_children():
            grandchildren = grandchildren | FamilyMember.objects.filter(pk=grandchild.pk)
    grandchildren = grandchildren.distinct()

    return render(request, 'accounts/family_detail.html', {
        'member': member,
        'siblings': siblings,
        'children': children,
        'cousins': cousins,
        'nieces_nephews': nieces_nephews,
        'grandchildren': grandchildren,
    })


@login_required
def add_member(request):
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save(commit=False)
            member.user = request.user
            member.save()
            return redirect('family_list')
    else:
        form = FamilyMemberForm()
    return render(request, 'accounts/add_member.html', {'form': form})


def _build_member_dict(member):
    return {
        'id': member.pk,
        'name': str(member),
        'full_name': f"{member.first_name} {member.middle_name} {member.last_name}".strip(),
        'gender': member.gender,
        'dob': str(member.date_of_birth) if member.date_of_birth else '',
        'dod': str(member.date_of_death) if member.date_of_death else '',
        'is_deceased': member.is_deceased,
        'age': member.age,
        'spouse_id': member.spouse.pk if member.spouse else None,
        'spouse_name': f"{member.spouse.first_name} {member.spouse.last_name}" if member.spouse else '',
        'photo': member.photo.url if member.photo else '',
    }


def _build_descendants(member, visited=None):
    if visited is None:
        visited = set()
    if member.pk in visited:
        return None
    visited.add(member.pk)
    children = member.get_children()
    data = _build_member_dict(member)
    data['children'] = [
        node for node in (_build_descendants(c, visited) for c in children)
        if node is not None
    ]
    return data


def _build_ancestors(member, depth=0):
    if depth > 4:
        return None
    data = _build_member_dict(member)
    data['father'] = _build_ancestors(member.father, depth + 1) if member.father else None
    data['mother'] = _build_ancestors(member.mother, depth + 1) if member.mother else None
    return data


def _tree_json_response(member):
    return {
        'focused_id': member.pk,
        'focused_name': str(member),
        'tree': _build_descendants(member),
        'ancestors': _build_ancestors(member),
        'all_members': [
            {
                'id': m.pk,
                'name': str(m),
                'gender': m.gender,
                'last_name': m.last_name,
                'photo': m.photo.url if m.photo else '',
            }
            for m in FamilyMember.objects.all()
        ]
    }


@login_required
def family_tree_json(request):
    member_id = request.GET.get('id')
    if member_id:
        try:
            member = FamilyMember.objects.get(pk=member_id)
        except FamilyMember.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
    else:
        member = FamilyMember.objects.filter(father__isnull=True).order_by('date_of_birth').first()
        if not member:
            member = FamilyMember.objects.first()
        if not member:
            return JsonResponse({'tree': None, 'ancestors': None})
    return JsonResponse(_tree_json_response(member))


def public_tree_json(request, username):
    from django.contrib.auth.models import User as AuthUser
    try:
        user = AuthUser.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
    except (AuthUser.DoesNotExist, UserProfile.DoesNotExist):
        return JsonResponse({'error': 'Not found'}, status=404)
    if not profile.tree_public:
        return JsonResponse({'error': 'This tree is private'}, status=403)
    member_id = request.GET.get('id')
    if member_id:
        try:
            member = FamilyMember.objects.get(pk=member_id)
        except FamilyMember.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
    else:
        member = FamilyMember.objects.filter(father__isnull=True).order_by('date_of_birth').first()
        if not member:
            member = FamilyMember.objects.first()
        if not member:
            return JsonResponse({'tree': None, 'ancestors': None})
    return JsonResponse(_tree_json_response(member))


def public_tree(request, username):
    from django.contrib.auth.models import User as AuthUser
    try:
        user = AuthUser.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
    except (AuthUser.DoesNotExist, UserProfile.DoesNotExist):
        return render(request, 'accounts/public_tree_error.html', {'reason': 'not_found'})
    if not profile.tree_public:
        return render(request, 'accounts/public_tree_error.html', {'reason': 'private'})
    return render(request, 'accounts/public_tree.html', {'tree_owner': user})


@login_required
def toggle_privacy(request):
    if request.method == 'POST':
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.tree_public = not profile.tree_public
        profile.save()
    return redirect(request.POST.get('next', 'visual_tree'))


@login_required
def invite_send(request):
    sent = False
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            invite = Invite.objects.create(invited_by=request.user, email=email)
            invite_url = request.build_absolute_uri(
                f"/accounts/register/?token={invite.token}"
            )
            # Send via Resend HTTP API
            import resend
            resend.api_key = os.environ.get('RESEND_API_KEY', '')
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": email,
                "subject": "You are invited to join Link Root",
                "text": (
                    f"Hi,\n\n"
                    f"{request.user.username} has invited you to join Link Root "
                    f"— a family tree app.\n\n"
                    f"Click the link below to create your account:\n{invite_url}\n\n"
                    f"Tashi Delek!"
                ),
            })
            sent = True
    invites = Invite.objects.filter(invited_by=request.user).order_by('-created_at')
    return render(request, 'accounts/invite_send.html', {'sent': sent, 'invites': invites})


@login_required
def profile(request):
    prof, _ = UserProfile.objects.get_or_create(user=request.user)
    invites = Invite.objects.filter(invited_by=request.user).order_by('-created_at')
    total_members = FamilyMember.objects.count()
    return render(request, 'accounts/profile.html', {
        'profile': prof,
        'invites': invites,
        'total_members': total_members,
    })


@login_required
def visual_tree(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/visual_tree.html', {'profile': profile})


@login_required
def edit_member(request, pk):
    member = get_object_or_404(FamilyMember, pk=pk)
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            return redirect('family_detail', pk=pk)
    else:
        form = FamilyMemberForm(instance=member)
    return render(request, 'accounts/edit_member.html', {'form': form, 'member': member})