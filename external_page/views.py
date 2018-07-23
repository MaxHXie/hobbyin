from django.conf import settings
from django.shortcuts import render, redirect
from external_page.models import Hobby, Instructor, InstructorMessage
from hobby_event.models import HobbyEvent
from django.contrib import messages
from django.core.mail import send_mail
from smtplib import SMTPException
from django.contrib.auth.models import User
from .forms import InstructorForm, ContactInstructorForm
from django.contrib.auth import logout as logout_function

def check_user_valid_profile(request):
    current_user = request.user
    try:
        instructor = Instructor.objects.get(user=current_user)
        if instructor.valid_profile:
            return True
        else:
            return False
    except Instructor.DoesNotExist:
        create_instructor(current_user)
        return False

def create_instructor(current_user):
    instructor = Instructor.objects.create(user=current_user)
    instructor.save()
    return instructor

def compose_message(message_object):
    if message_object.email == None:
        email = ""
    else:
        email = "Email: " + message_object.email + " \n"

    if message_object.telephone == None:
        telephone = ""
    else:
        telephone = "Telefon: " + message_object.telephone + "\n"

    if message_object.message == None:
        message_text = ""
    else:
        message_text = "[MEDDELANDE]" + " \n\n" + message_object.message + " \n\n"

    subject =   "[Hobbyin] Du har fått en kundförfrågan!"
    message =   ["[KUNDINFORMATION]" + " \n\n",
                "Namn: " + message_object.first_name + " \n",
                email,
                telephone,
                " \n\n",
                message_text,
                "Med vänlig hälsning" + " \n\n",
                message_object.first_name]

    message = "".join(message)
    return subject, message

# Create your views here.
def index(request):
    if request.user.is_authenticated and not check_user_valid_profile(request):
        messages.info(request, 'Det saknas fortfarande nödvändig information om dig. Fyll i dem för att komma igång.')
        return edit_profile(request)

    hobbies = Hobby.objects.all()
    if len(hobbies) == 0:
        hobbies = None
    return render(request, 'landing_page.html', context={'hobbies': hobbies})



def terms_of_use(request):
    return render(request, 'other_templates/terms_of_use.html')



def logout(request):
    logout_function(request)
    messages.info(request, 'Du har blivit utloggad')
    return index(request)



def settings(request):
    if request.user.is_authenticated:
        return render(request, 'settings_page.html', {'this_user': request.user})
    else:
        return index(request)



def instructors(request, hobby_name):
    if hobby_name == "malning":
        hobby_name = "målning"
    try:
        hobby = Hobby.objects.get(hobby_name=hobby_name)
        instructors = hobby.instructor_set.all()
        hobby_events = HobbyEvent.objects.filter(hobby=hobby, is_active=True, is_accepted=True, is_hidden=False)
    except Hobby.DoesNotExist:
        hobby = None
        hobby_events = None
        instructors = []
    return render(request, 'instructors_page.html', context={'hobby': hobby, 'hobby_name': hobby_name, 'instructors': instructors, 'hobby_events': hobby_events})



def profile_with_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        error_message = "Existerar inte"
        messages.error(request, 'Den här profilen existerar inte längre')
        return render(request, 'profile_page.html', context={'error_message': error_message, 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})

    try:
        instructor = Instructor.objects.get(user=user)
    except Instructor.DoesNotExist:
        error_message = "Existerar inte"
        messages.error(request, 'Den här profilen existerar inte längre')
        return render(request, 'profile_page.html', context={'error_message': error_message, 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})

    hobby_list = Hobby.objects.filter(instructor=instructor)

    if len(hobby_list) == 1:
        return profile_with_user_hobby(request, user_id, hobby_list[0])

    return render(request, 'profile_page.html', context={'hobby_list': hobby_list, 'instructor':instructor, 'this_user': user, 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})



def profile_with_user_hobby(request, user_id, hobby):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        error_message = "Existerar inte"
        messages.error(request, 'Den här profilen existerar inte längre')
        return render(request, 'profile_page.html', context={'error_message': error_message, 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})

    try:
        instructor = Instructor.objects.get(user=user)
    except Instructor.DoesNotExist:
        error_message = "Existerar inte"
        messages.error(request, 'Den här profilen existerar inte längre')
        return render(request, 'profile_page.html', context={'error_message': error_message, 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})

    try:
        hobby = Hobby.objects.get(hobby_name=hobby)
    except Hobby.DoesNotExist:
        return profile_with_user(request, user_id)

    hobby_list = Hobby.objects.filter(instructor=instructor)
    if hobby not in hobby_list:
        return profile_with_user(request, user_id)

    #Contact the teacher
    if request.method == "POST":
        message_object = InstructorMessage.objects.create(to_user=user)
        form = ContactInstructorForm(request.POST, instance=message_object)
        if form.is_valid():
            form.save()
            try:
                subject, message = compose_message(message_object)
                to_list = [user.instructor.email]
                from_email = "noreply@hobbyin.se"
                send_mail(subject, message, from_email, to_list)
                message_object.message_sent = True
                message_object.save()
                messages.success(request, 'Ditt meddelande har skickats!')
            except SMTPException:
                messages.error(request, 'Vi lyckades inte skicka ditt meddelande, vänta ett par minuter och försök igen.')
        else:
            messages.error(request, 'Ditt meddelande skickades inte iväg, dubbelkolla så att allting är rätt.')
        return render(request, 'profile_page.html', context={'hobby': hobby, 'instructor':instructor, 'this_user': user, 'form': form, 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})

    else:
        form = ContactInstructorForm()
        return render(request, 'profile_page.html', context={'hobby': hobby, 'instructor': instructor, 'this_user': user, 'form': form, 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})



def my_profile(request):
    ## User is redirected here upon LOGIN
    if request.user.is_authenticated and request.user.instructor:
        if not check_user_valid_profile(request):
            messages.info(request, 'Det saknas fortfarande nödvändig information om dig. Fyll i dem för att komma igång.')
            return edit_profile(request)
        else:
            return profile_with_user(request, request.user.id)

    else:
        messages.error(request, 'Du är inte inloggad som en instruktör')
        return redirect('account_login')



def edit_profile(request):
    if request.user.is_authenticated and request.user.instructor:
        current_user = request.user
        try:
            instructor = Instructor.objects.get(user=current_user)
        except Instructor.DoesNotExist:
            instructor = create_instructor(current_user)

        if request.method == "POST":
            form = InstructorForm(request.POST, request.FILES, instance=instructor)
            if form.is_valid():
               form.save()
               instructor.valid_profile = True
               instructor.save()
               messages.success(request, 'Din profil är ändrad.')
               request.method = "GET"
               return my_profile(request)
            else:
                messages.error(request, 'Din profil ändrades inte. Dubbelkolla gärna att allting är rätt.')
                return render(request, 'edit_profile_page.html', context={'form': form})
        else:
            form = InstructorForm(None, instance=instructor)
            return render(request, 'edit_profile_page.html', context={'form': form})

    else:
        messages.error(request, 'Du är inte inloggad som en instruktör')
        return redirect('account_login')
