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
            return redirect('dashboard')
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
        form = FamilyMemberForm(request.POST)
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
    """Returns all family members as JSON for the visual tree."""

    def build_node(member, visited=None):
        if visited is None:
            visited = set()
        if member.pk in visited:
            return None
        visited.add(member.pk)

        children = member.get_children()
        return {
            'id': member.pk,
            'name': f"{member.first_name} {member.last_name}",
            'gender': member.gender,
            'dob': str(member.date_of_birth) if member.date_of_birth else '',
            'spouse': str(member.spouse) if member.spouse else '',
            'children': [
                node for node in (build_node(child, visited) for child in children)
                if node is not None
            ],
        }

    # Root members are those with no father recorded
    roots = FamilyMember.objects.filter(father__isnull=True)
    tree_data = [build_node(m) for m in roots]

    return JsonResponse({'tree': tree_data})


@login_required
def visual_tree(request):
    return render(request, 'accounts/visual_tree.html')