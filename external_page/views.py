import json
import urllib
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Hobby, Instructor, Customer, InstructorMessage, VisitInstructor, InstructorSearch, Follower
from hobby_event.models import HobbyEvent
from django.contrib import messages
from django.core.mail import send_mail
from smtplib import SMTPException
from django.contrib.auth.models import User
from allauth.account.views import SignupView
from .forms import InstructorForm, CustomerForm, InstructorSignUpForm, CustomerSignUpForm
from django.contrib.auth import logout as logout_function
import hobbyin.functions as functions

class InstructorSignUp(SignupView):
    template_name = 'custom_allauth/signup_instructor.html'
    form_class = InstructorSignUpForm
    redirect_field_name = 'next'
    view_name = 'instructor_sign_up'

    def get_context_data(self, **kwargs):
        ret = super(InstructorSignUp, self).get_context_data(**kwargs)
        ret.update(self.kwargs)
        return ret

class CustomerSignUp(SignupView):
    template_name = 'custom_allauth/signup_customer.html'
    form_class = CustomerSignUpForm
    redirect_field_name = 'next'
    view_name = 'customer_sign_up'

    def get_context_data(self, **kwargs):
        ret = super(CustomerSignUp, self).get_context_data(**kwargs)
        ret.update(self.kwargs)
        return ret

def compose_message(profile, message_text):
    subject =   "[Hobbyin] Du har fått en kundförfrågan!"
    message =   ["[KUNDINFORMATION]" + " \n\n",
                "Namn: " + profile.first_name + " " + profile.last_name + " \n",
                "Email: " + profile.email,
                "Telefonnummer: " + profile.telephone,
                " \n\n",
                "[MEDDELANDE]" + " \n\n" + message_text + " \n\n",
                "Med vänlig hälsning" + " \n\n",
                profile.first_name + " " + profile.last_name]

    message = "".join(message)
    return subject, message

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        status = functions.check_user_valid_profile(request)
        if status == 'not_valid':
            request.method = "GET"
            messages.info(request, 'Det saknas fortfarande nödvändig information om dig. Fyll i dem för att komma igång.')
            return edit_profile(request)
        elif status == 'not_active':
            messages.error(request, 'Ditt konto är inte aktivt, kontakta maxhxie@gmail.com så hjälper vi dig.')
            return logout(request)

    hobbies = Hobby.objects.all()
    if len(hobbies) == 0:
        hobbies = None

    else:
        hobby_event_dictionary = {}
        hobby_instructor_dictionary = {}

        for hobby in hobbies:
            hobby_events = HobbyEvent.objects.filter(hobby=hobby, is_active=True, is_accepted=True, is_hidden=False)
            hobby_events = [event for event in hobby_events if event.has_happened == False]
            instructors = Instructor.objects.filter(hobbies=hobby, valid_profile=True, is_private_instructor=True, is_active=True)
            hobby_event_dictionary[hobby.hobby_name] = hobby_events
            hobby_instructor_dictionary[hobby.hobby_name] = instructors

    return render(request, 'landing_page.html', context={'hobbies': hobbies, 'hobby_event_dictionary': hobby_event_dictionary, 'hobby_instructor_dictionary': hobby_instructor_dictionary})



def terms_of_use(request):
    return render(request, 'other_templates/terms_of_use.html')



def integrity(request):
    return render(request, 'other_templates/integrity.html')



def logout(request):
    logout_function(request)
    messages.info(request, 'Du har blivit utloggad')
    return index(request)



def settings(request):
    this_user = functions.get_this_user(request)
    if this_user != None:
        return render(request, 'settings_page.html', {'this_user': this_user})
    else:
        return index(request)



def instructors(request, hobby_name):
    this_user = functions.get_this_user(request)
    input_zip_code = request.GET.get('input_zip_code')

    if hobby_name == "malning":
        hobby_name = "målning"
    try:
        hobby = Hobby.objects.get(hobby_name=hobby_name)
        InstructorSearch.objects.create(user=this_user, search_string=hobby_name, zip_code_search=input_zip_code)
        instructors = Instructor.objects.filter(hobbies=hobby, valid_profile=True, is_private_instructor=True, is_active=True)
        hobby_events = HobbyEvent.objects.filter(hobby=hobby, is_active=True, is_accepted=True, is_hidden=False)
        hobby_events = [event for event in hobby_events if event.has_happened == False]
    except Hobby.DoesNotExist:
        hobby = None
        hobby_events = None
        instructors = []

    instructors = list(instructors)
    worked, instructors, error = functions.sort_by_proximity(instructors, input_zip_code, request)
    if worked == False and error != None:
        messages.error(request, error)

    return render(request, 'instructors_page.html', context={'hobby': hobby, 'hobby_name': hobby_name, 'instructors': instructors, 'hobby_events': hobby_events})



def profile_with_user(request, user_id):
    if request.user.is_authenticated:
        status = functions.check_user_valid_profile(request)
        if status == 'not_valid':
            request.method = "GET"
            messages.info(request, 'Det saknas fortfarande nödvändig information om dig. Fyll i dem för att komma igång.')
            return edit_profile(request)
        elif status == 'not_active':
            messages.error(request, 'Ditt konto är inte aktivt, kontakta maxhxie@gmail.com så hjälper vi dig.')
            return logout(request)

        this_user = functions.get_this_user(request)

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Den här profilen existerar inte längre.')
        return render(request, 'profile_page.html', context={'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})

    profile_model = functions.get_profile_model(user)
    try:
        profile = profile_model.objects.get(user=user)
    except profile_model.DoesNotExist:
        messages.error(request, 'Den här profilen existerar inte längre.')
        return render(request, 'profile_page.html', context={'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})
    if profile.is_active == False:
        messages.error(request, 'Den här profilen är avaktiverad.')
        return render(request, 'profile_page.html', context={'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})

    if profile_model == Instructor:
        hobby_list = Hobby.objects.filter(instructor=profile)
        if len(hobby_list) == 1:
            return profile_with_user_hobby(request, user_id, hobby_list[0])
    else:
        hobby_list = []

    return render(request, 'profile_page.html', context={'hobby_list': hobby_list, 'profile':profile, 'this_user': this_user, 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})



def profile_with_user_hobby(request, user_id, hobby):
    if request.user.is_authenticated:
        status = functions.check_user_valid_profile(request)
        if status == 'not_valid':
            request.method = "GET"
            messages.info(request, 'Det saknas fortfarande nödvändig information om dig. Fyll i dem för att komma igång.')
            return edit_profile(request)
        elif status == 'not_active':
            messages.error(request, 'Ditt konto är inte aktivt, kontakta maxhxie@gmail.com så hjälper vi dig.')
            return logout(request)

    try:
        profile_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Den här profilen existerar inte längre')
        return render(request, 'profile_page.html', context={'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})

    try:
        instructor = Instructor.objects.get(user=profile_user)
    except Instructor.DoesNotExist:
        messages.error(request, 'Den här profilen existerar inte längre')
        return render(request, 'profile_page.html', context={'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})

    try:
        hobby = Hobby.objects.get(hobby_name=hobby)
    except Hobby.DoesNotExist:
        return profile_with_user(request, user_id)

    this_user = functions.get_this_user(request)
    VisitInstructor.objects.create(user=this_user, instructor=instructor, hobby=hobby)

    hobby_list = Hobby.objects.filter(instructor=instructor)
    if hobby not in hobby_list:
        return profile_with_user(request, user_id)

    if len(Follower.objects.filter(instructor=profile_user.instructor, follower=this_user)) > 0:
        following = True
    else:
        following = False

    followers = len(Follower.objects.filter(instructor=profile_user.instructor))

    return render(request, 'profile_page.html', context={'hobby': hobby, 'profile':instructor, 'this_user': this_user, 'profile_user': profile_user, 'following': following, 'followers': followers, 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})



def send_instructor_message(request, user_id, hobby):
    try:
        instructor_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Den här profilen existerar inte längre')
        return profile_with_user_hobby(request, user_id, hobby)

    if request.user.is_authenticated:
        if request.method == "POST":
            message_text = request.POST.get('message_text')
            if len(message_text) > 2500:
                messages.error(request, 'Ditt medddelande får inte vara längre än 2500 tecken')
                return profile_with_user_hobby(request, user_id, hobby)
            profile_model = functions.get_profile_model(request.user)
            if profile_model != None:
                profile = profile_model.objects.get(user=request.user)
                if instructor_user == profile.user:
                    messages.error(request, 'Du kan inte skicka meddelanden till dig själv.')
                    return profile_with_user_hobby(request, user_id, hobby)
                message_object = InstructorMessage.objects.create(to_user=instructor_user, first_name=profile.first_name, last_name=profile.last_name, email=profile.email, telephone=profile.telephone, message=message_text)
                mail_subject, mail_message = compose_message(profile, message_text)
                try:
                    send_mail(mail_subject, mail_message, 'hobbyin.se@gmail.com', [instructor_user.email])
                    message_objects.message_sent = True
                    message_objects.save()
                except SMTPException:
                    messages.error(request, 'Ditt meddelande kunde inte skickas iväg.')
                    return profile_with_user_hobby(request, user_id, hobby)
                messages.success(request, 'Ditt meddelande har blivit skickat.')
                return profile_with_user_hobby(request, user_id, hobby)
            else:
                messages.error(request, 'Något gick fel. Kontakta oss på maxhxie@gmail.com så hjälper vi dig.')
                return logout(request)
        else:
            messages.error(request, "Ditt meddelande skickades inte.")
            return profile_with_user_hobby(request, user_id, hobby)
    else:
        messages.error(request, "Du måste vara inloggad för att skicka meddelanden.")
        return profile_with_user_hobby(request, user_id_hobby)



def my_profile(request):
    ## User is redirected here upon LOGIN
    this_user = functions.get_this_user(request)
    if this_user != None:
        status = functions.check_user_valid_profile(request)
        if status == 'not_valid':
            request.method = "GET"
            messages.info(request, 'Det saknas fortfarande nödvändig information om dig. Fyll i dem för att komma igång.')
            return edit_profile(request)
        elif status == 'not_active':
            messages.error(request, 'Ditt konto är inte aktivt, kontakta maxhxie@gmail.com så hjälper vi dig.')
            return logout(request)
        else:
            if functions.is_instructor(request) or functions.is_customer(request):
                return profile_with_user(request, this_user.id)
            else:
                messages.error(request, 'Något gick väldigt fel kontakta maxhxie@gmail.com så hjälper vi dig')
                return logout(request)
    else:
        messages.error(request, 'Du är inte inloggad')
        return redirect('account_login')



def edit_profile(request):
    this_user = functions.get_this_user(request)
    if this_user != None:

        if functions.is_instructor(request):
            account_form = InstructorForm
            account_obj = this_user.instructor
        elif functions.is_customer(request):
            account_form = CustomerForm
            account_obj = this_user.customer
        else:
            messages.error(request, 'Något gick väldigt fel. Kontakta maxhxie@gmail.com för hjälp.')
            return index(request)

        if request.method == "POST":
            form = account_form(request.POST, request.FILES, instance=account_obj)
            if form.is_valid():
               form.save()
               account_obj.valid_profile = True
               account_obj.save()
               messages.success(request, 'Din profil är ändrad.')
               request.method = "GET"
               return my_profile(request)
            else:
                messages.error(request, 'Din profil ändrades inte. Dubbelkolla gärna att allting är rätt.')
                return render(request, 'edit_profile_page.html', context={'form': form})
        else:
            form = account_form(None, instance=account_obj)
            return render(request, 'edit_profile_page.html', context={'form': form})

    else:
        messages.error(request, 'Du är inte inloggad som en instruktör')
        return redirect('account_login')



def follow_instructor(request):
    if request.user.is_authenticated:
        this_user = functions.get_this_user(request)
        profile_model = functions.get_profile_model(this_user)
        if request.method == "POST":
            user_id = request.POST.get('user_id')
        else:
            return my_profile(request)

        try:
            instructor_user = User.objects.get(pk=user_id)
            temp_model = functions.get_profile_model(instructor_user)
            if temp_model != Instructor:
                messages.error(request, 'Du kan bara följa instruktörer.')
                return profile_with_user(request, user_id)
        except User.DoesNotExist:
            messages.error(request, 'Den här profilen existerar inte längre.')
            return profile_with_user(request, user_id)

        try:
            Follower.objects.get(instructor=instructor_user.instructor, follower=this_user)
            messages.error(request, 'Du följer redan ' + instructor_user.instructor.first_name + ' ' + instructor_user.instructor.last_name + '.')
            return profile_with_user(request, user_id)
        except Follower.DoesNotExist:
            pass

        if profile_model == None:
            messages.error(request, 'Du är inte behörig att följa instruktörer.')
            return profile_with_user(request, user_id)
        else:
            profile_model.objects.get(user=this_user)
            if this_user == instructor_user:
                messages.error(request, 'Du kan inte följa dig själv.')
                return profile_with_user(request, user_id)
            else:
                Follower.objects.create(instructor=instructor_user.instructor, follower=this_user)
                messages.success(request, 'Du följer nu ' + instructor_user.instructor.first_name + ' ' + instructor_user.instructor.last_name)
                return profile_with_user(request, user_id)

    else:
        messages.error(request, 'Du måste vara inloggad')
        return profile_with_user(request, user_id)

def unfollow_instructor(request):
    if request.user.is_authenticated:
        this_user = functions.get_this_user(request)
        profile_model = functions.get_profile_model(this_user)
        if request.method == "POST":
            user_id = request.POST.get('user_id')
        else:
            return my_profile(request)

        try:
            instructor_user = User.objects.get(pk=user_id)
            temp_model = functions.get_profile_model(instructor_user)
            if temp_model != Instructor:
                messages.error(request, 'Du kan bara avfölja instruktörer.')
                return profile_with_user(request, user_id)
        except User.DoesNotExist:
            messages.error(request, 'Den här profilen existerar inte längre.')
            return profile_with_user(request, user_id)

        if profile_model == None:
            messages.error(request, 'Du är inte behörig att avfölja instruktörer.')
            return profile_with_user(request, user_id)
        else:
            profile_model.objects.get(user=this_user)
            if this_user == instructor_user:
                messages.error(request, 'Du kan inte avfölja dig själv.')
                return profile_with_user(request, user_id)
            else:
                follow_objects = Follower.objects.filter(instructor=instructor_user.instructor, follower=this_user)
                if len(follow_objects) == 0:
                    messages.error(request, 'Du följer redan inte den här instruktören.')
                    return profile_with_user(request, user_id)
                else:
                    for object in follow_objects:
                        object.delete()
                messages.info(request, 'Du har nu avföljt ' + instructor_user.instructor.first_name + ' ' + instructor_user.instructor.last_name)
                return profile_with_user(request, user_id)

    else:
        messages.error(request, 'Du måste vara inloggad')
        return profile_with_user(request, user_id)
