from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import FamilyMember
from .forms import FamilyMemberForm


def home(request):
    return render(request, 'accounts/home.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
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
    members = FamilyMember.objects.all()
    return render(request, 'accounts/family_list.html', {'members': members})


@login_required
def family_detail(request, pk):
    member = get_object_or_404(FamilyMember, pk=pk)
    children = member.get_children()

    # Siblings share the same father or mother
    siblings = FamilyMember.objects.none()
    if member.father:
        siblings = siblings | FamilyMember.objects.filter(father=member.father).exclude(pk=pk)
    if member.mother:
        siblings = siblings | FamilyMember.objects.filter(mother=member.mother).exclude(pk=pk)
    siblings = siblings.distinct()

    # Relatives share the same grandparent
    relatives = FamilyMember.objects.none()
    if member.father and member.father.father:
        relatives = relatives | FamilyMember.objects.filter(
            father__father=member.father.father
        ).exclude(pk=pk)

    return render(request, 'accounts/family_detail.html', {
        'member': member,
        'siblings': siblings,
        'children': children,
        'relatives': relatives,
    })


@login_required
def add_member(request):
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST, request.FILES)  # ← request.FILES added
        if form.is_valid():
            member = form.save(commit=False)
            member.user = request.user
            member.save()
            return redirect('family_list')
    else:
        form = FamilyMemberForm()
    return render(request, 'accounts/add_member.html', {'form': form})


@login_required
def family_tree_json(request):
    member_id = request.GET.get('id')

    def build_descendants(member, visited=None):
        if visited is None:
            visited = set()
        if member.pk in visited:
            return None
        visited.add(member.pk)
        children = member.get_children()
        return {
            'id': member.pk,
            'name': str(member),
            'full_name': f"{member.first_name} {member.middle_name} {member.last_name}".strip(),
            'gender': member.gender,
            'dob': str(member.date_of_birth) if member.date_of_birth else '',
            'spouse_id': member.spouse.pk if member.spouse else None,
            'spouse_name': f"{member.spouse.first_name} {member.spouse.last_name}" if member.spouse else '',
            'photo': member.photo.url if member.photo else '',
            'children': [
                node for node in (build_descendants(c, visited) for c in children)
                if node is not None
            ],
        }

    def build_ancestors(member, depth=0):
        if depth > 4:
            return None
        return {
            'id': member.pk,
            'name': str(member),
            'gender': member.gender,
            'dob': str(member.date_of_birth) if member.date_of_birth else '',
            'spouse_id': member.spouse.pk if member.spouse else None,
            'spouse_name': f"{member.spouse.first_name} {member.spouse.last_name}" if member.spouse else '',
            'photo': member.photo.url if member.photo else '',
            'father': build_ancestors(member.father, depth + 1) if member.father else None,
            'mother': build_ancestors(member.mother, depth + 1) if member.mother else None,
        }

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

    return JsonResponse({
        'focused_id': member.pk,
        'focused_name': str(member),
        'tree': build_descendants(member),
        'ancestors': build_ancestors(member),
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
    })


@login_required
def visual_tree(request):
    return render(request, 'accounts/visual_tree.html')


@login_required
def edit_member(request, pk):
    member = get_object_or_404(FamilyMember, pk=pk)
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST, request.FILES, instance=member)  # ← request.FILES added
        if form.is_valid():
            form.save()
            return redirect('family_detail', pk=pk)
    else:
        form = FamilyMemberForm(instance=member)
    return render(request, 'accounts/edit_member.html', {'form': form, 'member': member})