from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
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
        children = FamilyMember.objects.filter(
            father_name=f"{member.first_name} {member.last_name}"
        ) | FamilyMember.objects.filter(
            father_name=f"{member.first_name} {member.middle_name} {member.last_name}"
        ) | FamilyMember.objects.filter(
            mother_name=f"{member.first_name} {member.last_name}"
        ) | FamilyMember.objects.filter(
            mother_name=f"{member.first_name} {member.middle_name} {member.last_name}"
        )
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
    member = FamilyMember.objects.get(pk=pk)
    siblings = FamilyMember.objects.filter(
        father_name=member.father_name
    ).exclude(pk=pk)
    children = FamilyMember.objects.filter(
        father_name=f"{member.first_name} {member.last_name}"
    ) | FamilyMember.objects.filter(
        father_name=f"{member.first_name} {member.middle_name} {member.last_name}"
    ) | FamilyMember.objects.filter(
        mother_name=f"{member.first_name} {member.last_name}"
    ) | FamilyMember.objects.filter(
        mother_name=f"{member.first_name} {member.middle_name} {member.last_name}"
    )
    relatives = FamilyMember.objects.filter(
        grandfather_name=member.grandfather_name
    ).exclude(pk=pk)
    return render(request, 'accounts/family_detail.html', {
        'member': member,
        'siblings': siblings,
        'children': children,
        'relatives': relatives,
    })

@login_required
def grandparent_detail(request, name):
    grandchildren = FamilyMember.objects.filter(
        grandfather_name=name
    ) | FamilyMember.objects.filter(
        grandmother_name=name
    )
    return render(request, 'accounts/grandparent_detail.html', {
        'grandparent_name': name,
        'grandchildren': grandchildren,
    })

@login_required
def parent_detail(request, name):
    children = FamilyMember.objects.filter(
        father_name=name
    ) | FamilyMember.objects.filter(
        mother_name=name
    )
    co_parent = None
    if children.exists():
        first_child = children.first()
        if first_child.father_name == name:
            co_parent = first_child.mother_name
        else:
            co_parent = first_child.father_name
    return render(request, 'accounts/parent_detail.html', {
        'parent_name': name,
        'co_parent': co_parent,
        'children': children,
    })

@login_required
def address_detail(request, address):
    members = FamilyMember.objects.filter(address=address)
    return render(request, 'accounts/address_detail.html', {
        'address': address,
        'members': members,
    })

@login_required
def add_member(request):
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('family_list')
    else:
        form = FamilyMemberForm()
    return render(request, 'accounts/add_member.html', {'form': form})

@login_required
def member_search(request, name):
    try:
        parts = name.split(' ')
        first_name = parts[0]
        last_name = parts[-1]
        member = FamilyMember.objects.filter(
            first_name=first_name,
            last_name=last_name
        ).first()
        if member:
            return redirect('family_detail', pk=member.pk)
        else:
            return render(request, 'accounts/not_found.html', {'name': name})
    except:
        return render(request, 'accounts/not_found.html', {'name': name})
    
@login_required
def visual_tree(request):
    members = FamilyMember.objects.all()
    return render(request, 'accounts/visual_tree.html', {'members': members})

@login_required
def visual_tree(request):
    all_members = FamilyMember.objects.all()

    def get_children(member):
        full_name = f"{member.first_name} {member.last_name}"
        full_name_middle = f"{member.first_name} {member.middle_name} {member.last_name}"
        return FamilyMember.objects.filter(
            father_name=full_name
        ) | FamilyMember.objects.filter(
            father_name=full_name_middle
        )

    def is_root(member):
        if not member.father_name:
            return True
        father_first = member.father_name.split(' ')[0]
        return not FamilyMember.objects.filter(first_name=father_first).exists()

    def build_tree(member):
        children = get_children(member)
        return {
            'member': member,
            'children': [build_tree(child) for child in children],
            'spouse': member.spouse_name if member.marital_status == 'Married' else None,
        }

    roots = [build_tree(m) for m in all_members if is_root(m)]

    return render(request, 'accounts/visual_tree.html', {'roots': roots})