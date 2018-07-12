from django.shortcuts import render, redirect
from external_page.models import Hobby, Instructor
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import InstructorForm

def first_time_login_and_create_instructor(request):
    current_user = request.user
    try:
        instructor = Instructor.objects.get(user=current_user)
        return False
    except Instructor.DoesNotExist:
        create_instructor(current_user)
        return True

def create_instructor(current_user):
    instructor = Instructor.objects.create(user=current_user)
    instructor.save()
    return instructor

# Create your views here.
def index(request):
    hobbies = Hobby.objects.all()
    if len(hobbies) == 0:
        hobbies = None
    return render(request, 'landing_page.html', context={'hobbies': hobbies})



def instructors(request, hobby_name):
    if hobby_name == "malning":
        hobby_name = "målning"
    try:
        hobby = Hobby.objects.get(hobby_name=hobby_name)
        instructors = hobby.instructor_set.all()
    except Hobby.DoesNotExist:
        hobby = None
        instructors = []
    return render(request, 'instructors_page.html', context={'hobby': hobby, 'hobby_name': hobby_name, 'instructors': instructors})



def profile_with_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        error_message = 'Den här profilen existerar inte längre'
        return render('profile_page.html', context={'error_message': error_message})

    try:
        instructor = Instructor.objects.get(user=user)
    except Instructor.DoesNotExist:
        error_message = 'Den här instruktören existerar inte'
        return render(request, 'profile_page.html', context={'error_message': error_message})

    hobby_list = Hobby.objects.filter(instructor=instructor)

    if len(hobby_list) == 1:
        return profile_with_user_hobby(request, user_id, hobby_list[0])

    return render(request, 'profile_page.html', context={'hobby_list': hobby_list, 'instructor':instructor, 'user': user})



def profile_with_user_hobby(request, user_id, hobby):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        error_message = 'Den här profilen existerar inte längre'
        return render('profile_page.html', context={'error_message': error_message})

    try:
        instructor = Instructor.objects.get(user=user)
    except Instructor.DoesNotExist:
        error_message = 'Den här instruktören existerar inte'
        return render(request, 'profile_page.html', context={'error_message': error_message})

    try:
        hobby = Hobby.objects.get(hobby_name=hobby)
    except Hobby.DoesNotExist:
        return profile_with_user(request, user_id)

    hobby_list = Hobby.objects.filter(instructor=instructor)
    if hobby not in hobby_list:
        return profile_with_user(request, user_id)

    return render(request, 'profile_page.html', context={'hobby': hobby, 'instructor':instructor, 'user': user})



def my_profile(request):
    ## User is redirected here upon LOGIN
    if request.user.is_authenticated:
        if first_time_login_and_create_instructor(request):
            return edit_profile(request)
        else:
            return profile_with_user(request, request.user.id)

    else:
        messages.error(request, 'Du är inte inloggad')
        return redirect('account_login')



def edit_profile(request):
    if request.user.is_authenticated:
        current_user = request.user
        try:
            instructor = Instructor.objects.get(user=current_user)
        except Instructor.DoesNotExist:
            instructor = create_instructor(current_user)

        if request.method == "POST":
            form = InstructorForm(request.POST, instance=instructor)
            if form.is_valid():
               form.save()
               messages.success(request, 'Din profil är ändrad.')
               return render(request, 'edit_profile_page.html', context={'form': form})
        else:
            form = InstructorForm(None, instance=instructor)
            return render(request, 'edit_profile_page.html', context={'form': form})

    else:
        messages.error(request, 'Du är inte inloggad')
        return redirect('account_login')
