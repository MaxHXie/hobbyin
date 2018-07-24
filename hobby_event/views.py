from django.shortcuts import render
from .forms import CreateEventForm, ContactEventForm
from .models import HobbyEvent, HobbyEventSignup
from external_page.models import Hobby, Instructor
from django.contrib import messages
import hobbyin.functions as functions
import random

colors = [(123,205,47), (119,172,236), (236,219,84), (240,237,229), (252,169,133), (209,255,244)]

# Create your views here.
def create_event(request):
    if request.user.is_authenticated and request.user.instructor:
        current_user = request.user
        try:
            instructor = Instructor.objects.get(user=current_user)
        except Instructor.DoesNotExist:
            instructor = create_instructor(current_user)
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
    if request.user.is_authenticated and request.user.instructor:
        this_user = request.user
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
        this_user = request.user
    else:
        this_user = None
    try:
        this_event = HobbyEvent.objects.get(pk=event_id)
    except HobbyEvent.DoesNotExist:
        messages.error(request, 'Det där evenemanget existerar inte längre.')
        return all_events(request)

    if this_event.event_host.user == this_user or (this_event.is_hidden == False and this_event.is_active == True and this_event.is_accepted == True and this_event.has_happened == False):
        if this_event.is_accepted == False:
            return create_event_terminal(request, this_event.id)

        if request.method == "POST":
            event_signup_object = HobbyEventSignup.objects.create(hobby_event=this_event)
            form = ContactEventForm(request.POST, instance=event_signup_object)
            if form.is_valid():
                if this_event.is_active == True and this_event.is_accepted == True and this_event.hidden == False:
                    form.save()
                    messages.success(request, 'Nu är du anmäld till: "' + this_event.event_name + '"')
                else:
                    messages.error(request, 'Det här evenemanget verkar inte vara aktivt längre')
            else:
                messages.error(request, 'Du lyckades inte bli anmäld, dubbelkolla så att allting är rätt.')

            return render(request, 'single_event_page.html', context={'this_event': this_event, 'this_user': this_user, 'form': form, 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})

        else:
            form = ContactEventForm()
    else:
        if this_event.has_happened:
            messages.error(request, 'Det här evenemanget har passerat')
        else:
            messages.error(request, 'Det här evenemanget går inte längre att ses.')
        return all_events(request)

    return render(request, 'single_event_page.html', context={'this_event': this_event, 'this_user': this_user, 'form': form, 'spam_uri': 'https://www.spelapaintball.com/#wpcf7-f2197-o1'})



def all_events(request):
    """
    Filter and sort all events on five factors:
        1. is_active, is_accepted, is_hidden: Do not include events that does not meet these criteria.
        2. search_hobby_event: Filter away events that does not match the search string.
        3. event_id: Sort by having the most recent events first. (Secondary priority sort)
        4. event.has_happened: Do not include all events that already has happened.
        5. input_zip_code: Sort by having the closest events first. (Primary priority sort)
    """

    search_hobby_event = request.GET.get('search_hobby_event')
    input_zip_code = request.GET.get('input_zip_code')

    #Filter away events that does not match the search string.
    if search_hobby_event != None:
        event_list1 = HobbyEvent.objects.filter(event_name__icontains=search_hobby_event, is_active=True, is_accepted=True, is_hidden=False)
        event_list3 = HobbyEvent.objects.filter(city__icontains=search_hobby_event, is_active=True, is_accepted=True, is_hidden=False)
        event_list4 = HobbyEvent.objects.filter(city_district__icontains=search_hobby_event, is_active=True, is_accepted=True, is_hidden=False)
        try:
            hobby = Hobby.objects.get(hobby_name__iexact=search_hobby_event)
            event_list2 = HobbyEvent.objects.filter(hobby=hobby, is_active=True, is_accepted=True, is_hidden=False)
            temp_list = event_list1 | event_list2 | event_list3 | event_list4

        except Hobby.DoesNotExist:
            hobby = None
            event_list2 = None
            temp_list = event_list1 | event_list3 | event_list4

        event_list = temp_list.distinct()

        if len(event_list) == 0:
            messages.error(request, 'Vi kunde inte hitta några evenemang för den här hobbyn.')
            request.method = "GET"

    else:
        hobby = None
        event_list = HobbyEvent.objects.filter(is_active=True, is_accepted=True, is_hidden=False)

    #Sort by having the most recent events first. (Secondary priority sort)
    event_list = event_list.order_by('-id')

    #Do not include events that already has happened
    event_list = [event for event in event_list if event.has_happened == False]

    worked, event_list, error = functions.sort_by_proximity(event_list, input_zip_code, request)
    if worked == False and error != None:
        messages.error(request, error)

    return render(request, 'all_events_page.html', context={'event_list': event_list, 'hobby': hobby, 'search_hobby_event': search_hobby_event, 'input_zip_code': input_zip_code})



def my_events(request):
    if request.user.is_authenticated and request.user.instructor:
        this_instructors_events = HobbyEvent.objects.filter(event_host=request.user.instructor).order_by('-id')
        return render(request, 'my_events_page.html', context={'event_list': this_instructors_events})
    else:
        messages.error(request, 'Du är inte inloggad som instruktör.')
        return all_events(request)



def edit_event(request, event_id):
    if request.user.is_authenticated and request.user.instructor:
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
            return create_events(request)
    else:
        messages.error(request, 'Du är inte inloggad som instruktör.')
        return all_events(request)



def event_participators(request, event_id):
    if request.user.is_authenticated and request.user.instructor:
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
    if request.user.is_authenticated and request.user.instructor:
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
                return my_events(request)

            else:
                messages.error(request, 'Det gick inte att ställa in evenemanget, försök igen.')
                return single_event(request, event_id)
        else:
            messages.error(request, 'Du har inte tillgång till det där evenmanget. Dubbelkolla så att du är inloggad på rätt konto.')
            return all_events(request)
    else:
        messages.error(request, 'Du är inte inloggad som instruktör.')
        return all_events(request)
