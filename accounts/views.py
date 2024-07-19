from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from .forms import UserForm, GroupForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.paginator import Paginator

@login_required
def user_list(request):
    users = User.objects.all().order_by('username')
    
    # Pagination
    paginator = Paginator(users, 2)  # Show 10 items per page
    page_number = request.GET.get('page')  # Get the current page number
    page_obj = paginator.get_page(page_number)  # Get the page object for the current page

    context = {
        'title' : 'List of Groups',
        'page_obj' : page_obj
    }

    return render(request, 'accounts/user_list.html', context=context)

@login_required
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            form.save_m2m()
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'accounts/user_form.html', {'form': form})

@login_required
def group_list(request):

    # groups = Group.objects.all().values_list()
    groups = Group.objects.all().order_by('name')

    # Pagination
    paginator = Paginator(groups, 2)  # Show 10 items per page
    page_number = request.GET.get('page')  # Get the current page number
    page_obj = paginator.get_page(page_number)  # Get the page object for the current page

    # prepare the date to be rendered on HTML page
    context = {
        'title' : 'List of Groups',
        'page_obj' : page_obj
    }

    return render(request, 'accounts/group_list.html', context=context)

@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'accounts/group_form.html', {'form': form})


def login_view(request):

    if request.session.get('_auth_user_id'):
        return redirect('dashboard') 

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to dashboard
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})



@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')



def logout_view(request):
    logout(request)
    return redirect('login')