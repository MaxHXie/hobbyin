from django.shortcuts import render
from .forms import CreateEventForm
from .models import HobbyEvent, HobbyEventSignup, VisitHobbyEvent, EventSearch
from external_page.models import Hobby, Instructor
from external_page.views import edit_profile, logout
from django.contrib import messages
import hobbyin.functions as functions
import random

colors = [(123,205,47), (119,172,236), (236,219,84), (240,237,229), (252,169,133), (209,255,244)]

# Create your views here.
def create_event(request):
    if functions.is_instructor(request):
        status = functions.check_user_valid_profile(request)
        if status == 'not_valid':
            request.method = "GET"
            messages.info(request, 'Det saknas fortfarande nödvändig information om dig. Fyll i dem för att komma igång.')
            return edit_profile(request)
        elif status == 'not_active':
            messages.error(request, 'Ditt konto är inte aktivt, kontakta maxhxie@gmail.com så hjälper vi dig.')
            return logout(request)

        current_user = request.user
        if request.method == "POST":
            event_object = HobbyEvent.objects.create(event_host=instructor, hobby=instructor.hobbies, is_active=True)
            color = random.choice(colors)
            event_object.event_color_red = color[0]
            event_object.event_color_green = color[1]
            event_object.event_color_blue = color[2]
            event_object.save()
            form = CreateEventForm(request.POST, instance=event_object)
            if form.is_valid():
                form.save()
                messages.info(request, 'Sista steget, dubbelkolla så att all info är rätt.')
                request.method = "GET"
                return create_event_terminal(request, event_object.id)

            else:
                messages.error(request, 'Ditt evenemang kunde inte skapas. Dubbelkolla gärna så att allting är rätt.')
                return render(request, 'create_event_page.html', context={'form': form, 'type': 'create', 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})
        else:
            form = CreateEventForm()
            return render(request, 'create_event_page.html', context={'form': form, 'type': 'create', 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})

    else:
        messages.error(request, 'Du är inte inloggad som instruktör.')
        return all_events(request)



def create_event_terminal(request, event_id):
    if functions.is_instructor(request):
        this_user = functions.get_this_user(request)
        try:
            this_event = HobbyEvent.objects.get(pk=event_id)
        except HobbyEvent.DoesNotExist:
            messages.error(request, 'Där gick något snett, försök igen.')
            return create_events(request)

        if this_event.event_host.user == this_user:
            if not this_event.is_accepted:
                if request.method == "POST":
                    this_event.is_accepted = True
                    this_event.save()
                    request.method = "GET"

                    messages.success(request, 'Ditt evenemang har skapats!')
                    return single_event(request, event_id)

                else:
                    return render(request, 'event_terminal_page.html', context={'this_event': this_event})
            else:
                messages.error(request, 'Du har redan publicerat det här evenemanget.')
                return single_event(request, event_id)
        else:
            messages.error(request, 'Du har inte tillgång till det där evenmanget. Dubbelkolla så att du är inloggad på rätt konto.')
            return create_events(request)
    else:
        messages.error(request, 'Du är inte inloggad som instruktör.')
        return all_events(request)



def single_event(request, event_id):
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
        this_event = HobbyEvent.objects.get(pk=event_id)
    except HobbyEvent.DoesNotExist:
        messages.error(request, 'Det där evenemanget existerar inte längre.')
        return all_events(request)

    VisitHobbyEvent.objects.create(user=this_user, hobby_event=this_event)

    if this_event.event_host.user == this_user or (this_event.is_hidden == False and this_event.is_active == True and this_event.is_accepted == True and this_event.has_happened == False):
        if this_event.is_accepted == False:
            return create_event_terminal(request, this_event.id)
    else:
        if this_event.has_happened:
            messages.error(request, 'Det här evenemanget har passerat')
        else:
            messages.error(request, 'Det här evenemanget går inte längre att ses.')
        return all_events(request)

    try:
        HobbyEventSignup.objects.get(hobby_event=this_event, user=this_user, is_success=True)
        signed_up = True
    except HobbyEventSignup.DoesNotExist:
        signed_up = False

    return render(request, 'single_event_page.html', context={'this_event': this_event, 'this_user': this_user, 'signed_up': signed_up, 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})



def all_events(request):
    """
    Filter and sort all events on five factors:
        1. is_active, is_accepted, is_hidden: Do not include events that does not meet these criteria.
        2. search_hobby_event: Filter away events that does not match the search string.
        3. event_id: Sort by having the most recent events first. (Secondary priority sort)
        4. event.has_happened: Do not include all events that already has happened.
        5. input_zip_code: Sort by having the closest events first. (Primary priority sort)
    """

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

    search_hobby_event = request.GET.get('search_hobby_event')
    input_zip_code = request.GET.get('input_zip_code')

    #Filter away events that does not match the search string.
    if search_hobby_event != None or input_zip_code != None:
        EventSearch.objects.create(user=this_user, search_string=search_hobby_event, zip_code_search=input_zip_code)

    if search_hobby_event != None and search_hobby_event != "":
        event_list1 = HobbyEvent.objects.filter(event_name__icontains=search_hobby_event, is_active=True, is_accepted=True, is_hidden=False)
        event_list3 = HobbyEvent.objects.filter(city__icontains=search_hobby_event, is_active=True, is_accepted=True, is_hidden=False)
        event_list4 = HobbyEvent.objects.filter(city_district__icontains=search_hobby_event, is_active=True, is_accepted=True, is_hidden=False)
        try:
            hobby = Hobby.objects.get(hobby_name__iexact=search_hobby_event)
            instructors_for_hobby = Instructor.objects.filter(hobbies=hobby, valid_profile=True, is_private_instructor=True, is_active=True)
            event_list2 = HobbyEvent.objects.filter(hobby=hobby, is_active=True, is_accepted=True, is_hidden=False)
            temp_list = event_list1 | event_list2 | event_list3 | event_list4

        except Hobby.DoesNotExist:
            hobby = None
            event_list2 = None
            instructors_for_hobby = []
            temp_list = event_list1 | event_list3 | event_list4

        event_list = temp_list.distinct()

        if len(event_list) == 0:
            messages.error(request, 'Vi kunde inte hitta några evenemang för den här hobbyn.')
            request.method = "GET"

    else:
        hobby = None
        instructors_for_hobby = []
        event_list = HobbyEvent.objects.filter(is_active=True, is_accepted=True, is_hidden=False)

    #Sort by having the most recent events first. (Secondary priority sort)
    event_list = event_list.order_by('-id')

    #Do not include events that already has happened
    event_list = [event for event in event_list if event.has_happened == False]

    worked, event_list, error = functions.sort_by_proximity(event_list, input_zip_code, request)
    if worked == False and error != None:
        messages.error(request, error)

    return render(request, 'all_events_page.html', context={'event_list': event_list, 'hobby': hobby, 'instructors_for_hobby': instructors_for_hobby, 'search_hobby_event': search_hobby_event, 'input_zip_code': input_zip_code})



def my_events(request):
    if request.user.is_authenticated:
        status = functions.check_user_valid_profile(request)
        if status == 'not_valid':
            request.method = "GET"
            messages.info(request, 'Det saknas fortfarande nödvändig information om dig. Fyll i dem för att komma igång.')
            return edit_profile(request)
        elif status == 'not_active':
            messages.error(request, 'Ditt konto är inte aktivt, kontakta maxhxie@gmail.com så hjälper vi dig.')
            return logout(request)

    if functions.is_instructor(request):
        this_instructors_events = HobbyEvent.objects.filter(event_host=request.user.instructor).order_by('-datetime')
        return render(request, 'my_events_page.html', context={'event_list': this_instructors_events})
    else:
        messages.error(request, 'Du är inte inloggad som instruktör.')
        return all_events(request)



def edit_event(request, event_id):
    if request.user.is_authenticated:
        status = functions.check_user_valid_profile(request)
        if status == 'not_valid':
            request.method = "GET"
            messages.info(request, 'Det saknas fortfarande nödvändig information om dig. Fyll i dem för att komma igång.')
            return edit_profile(request)
        elif status == 'not_active':
            messages.error(request, 'Ditt konto är inte aktivt, kontakta maxhxie@gmail.com så hjälper vi dig.')
            return logout(request)

    if functions.is_instructor(request):
        try:
            this_event = HobbyEvent.objects.get(pk=event_id)
        except HobbyEvent.DoesNotExist:
            messages.error(request, 'Där gick något snett, försök igen.')
            return create_events(request)

        this_instructors_events = HobbyEvent.objects.filter(event_host=request.user.instructor)
        if this_event in this_instructors_events:
            if request.method == "POST":
                form = CreateEventForm(request.POST, instance=this_event)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Ditt evenemang: "' + this_event.event_name + '" är nu ändrat.')
                    request.method = "GET"
                    return single_event(request, this_event.id)

                else:
                    messages.error(request, 'Ditt evenemang kunde inte ändras. Dubbelkolla gärna så att allting är rätt.')
                    return render(request, 'create_event_page.html', context={'form': form, 'type': 'edit', 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})
            else:
                form = CreateEventForm(instance=this_event)
                return render(request, 'create_event_page.html', context={'form': form, 'type': 'edit', 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})
        else:
            messages.error(request, 'Du har inte tillgång till det där evenmanget. Dubbelkolla så att du är inloggad på rätt konto.')
            return single_event(request, event_id)
    else:
        messages.error(request, 'Du är inte inloggad som instruktör.')
        return all_events(request)



def event_participators(request, event_id):
    if functions.is_instructor(request):
        try:
            this_event = HobbyEvent.objects.get(pk=event_id)
        except HobbyEvent.DoesNotExist:
            messages.error(request, 'Det där evenemanget existerar inte längre.')
            return all_events(request)

        if this_event.event_host == request.user.instructor:
            return render(request, 'event_participators_page.html', context={'this_event': this_event})

        else:
            messages.error(request, 'Du har inte tillgång till det där evenmanget. Dubbelkolla så att du är inloggad på rätt konto.')
            return all_events(request)
    else:
        messages.error(request, 'Du är inte inloggad som instruktör.')
        return all_events(request)




def hide_show_event(request, event_id):
    if functions.is_instructor(request):
        try:
            this_event = HobbyEvent.objects.get(pk=event_id)
        except HobbyEvent.DoesNotExist:
            messages.error(request, 'Det där evenemanget existerar inte längre.')
            return all_events(request)

        this_instructors_events = HobbyEvent.objects.filter(event_host=request.user.instructor)

        if this_event in this_instructors_events:
            if request.method == "POST":
                action_type = request.POST.get("action_type")
                if action_type == "show":
                    this_event.is_hidden = False
                    messages.info(request, 'Ditt evenemanng: "' + this_event.event_name + '" har nu blivit återställt!')
                elif action_type == "hide":
                    this_event.is_hidden = True
                    messages.info(request, 'Ditt evenemanng: "' + this_event.event_name + '" är nu gömt och låst.')

                this_event.save()
                request.method = "GET"
                return single_event(request, event_id)

            else:
                messages.error(request, 'Det gick inte att ställa in evenemanget, försök igen.')
                return single_event(request, event_id)
        else:
            messages.error(request, 'Du har inte tillgång till det där evenmanget. Dubbelkolla så att du är inloggad på rätt konto.')
            return all_events(request)
    else:
        messages.error(request, 'Du är inte inloggad som instruktör.')
        return all_events(request)



def signup_for_event(request, event_id):
    if request.user.is_authenticated:
        try:
            this_event = HobbyEvent.objects.get(pk=event_id)
        except HobbyEvent.DoesNotExist:
            messages.error(request, 'Det där evenemanget existerar inte längre.')
            return all_events(request)

        try:
            HobbyEventSignup.objects.get(hobby_event=this_event, user=request.user)
            messages.error(request, 'Du har redan anmält dig till det här evenemanget.')
            return single_event(request, event_id)
        except HobbyEventSignup.DoesNotExist:
            profile_model = functions.get_profile_model(request.user)
            if profile_model != None:
                profile = profile_model.objects.get(user=request.user)
                if profile.user != this_event.event_host.user:
                    HobbyEventSignup.objects.create(hobby_event=this_event, user=request.user, first_name=profile.first_name, last_name=profile.last_name, email=profile.email, telephone=profile.telephone, is_success=True)
                    messages.success(request, 'Du är nu anmäld till evenemanget.')
                    return single_event(request, event_id)
                else:
                    messages.error(request, 'Du kan inte anmäla dig till ditt egna evenemang.')
                    return single_event(request, event_id)
            else:
                messages.error(request, 'Något gick fel. Kontakta oss på maxhxie@gmail.com så hjälper vi dig.')
                return logout(request)
    else:
        messages.error(request, 'Du måste vara inloggad för att komma åt den här sidan.')
        return all_events(request)
