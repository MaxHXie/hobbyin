from django.db import models
from django.contrib.auth.models import User
from djangospam.akismet import moderator as akismet
from django.utils import timezone
from external_page.models import Instructor, Hobby

# Create your models here.
class HobbyEvent(models.Model):
    event_host = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
    )
    hobby = models.ForeignKey(
        Hobby,
        on_delete=models.CASCADE,
    )
    event_name = models.CharField(max_length=128, null=True, blank=False)
    datetime = models.DateTimeField(blank=False, null=True)
    city = models.CharField(max_length=64, null=True, blank=False)
    city_district = models.CharField(max_length=64, null=True, blank=False)
    zip_code = models.CharField(max_length=6, null=True, blank=False)
    address = models.CharField(max_length=64, null=True, blank=False)
    location_name = models.CharField(max_length=64, null=True, blank=True)
    price = models.PositiveIntegerField(default=0, blank=False, null=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    event_color_red = models.PositiveIntegerField(default=255, null=False)
    event_color_green =  models.PositiveIntegerField(default=255, null=False)
    event_color_blue = models.PositiveIntegerField(default=255, null=False)
    created_time = models.DateTimeField(auto_now_add=True, null=False, blank=True)

    @property
    def has_happened(self):
        return timezone.now() > self.datetime

    def __str__(self):
        try:
            string = '"' + self.event_name + '"' + " by " + self.event_host.first_name + " " + self.event_host.last_name
        except:
            string = "event_name_error"
        return string

class HobbyEventSignup(models.Model):
    hobby_event = models.ForeignKey(
        HobbyEvent,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
    )
    first_name = models.CharField(max_length=32, null=True, blank=False)
    last_name = models.CharField(max_length=32, null=True, blank=False)
    email = models.CharField(max_length=64, blank=True, null=True, unique=True)
    telephone = models.CharField(max_length=16, blank=True, null=True)
    is_success = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        try:
            string = self.first_name + " " + self.last_name + " to " + self.hobby_event.event_name
        except:
            string = "event_signup_name_error"
        return string

class VisitHobbyEvent(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )
    hobby_event = models.ForeignKey(
        HobbyEvent,
        on_delete=models.CASCADE,
    )
    datetime = models.DateTimeField(auto_now_add=True, blank=False, null=True)

    def __str__(self):
        if self.user == None:
            string = "Anonymous visited " + self.hobby_event.event_name
        else:
            string = self.user.email + " visited " + self.hobby_event.event_name
        return string

class EventSearch(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )
    search_string = models.CharField(max_length=128, null=True, blank=False)
    zip_code_search = models.CharField(max_length=128, null=True, blank=False)
    datetime = models.DateTimeField(auto_now_add=True, blank=False, null=True)

    def __str__(self):
        if self.user == None:
            this_user = 'Anonymous'
        else:
            this_user = '"' + self.user.email + '"'

        if self.search_string == None:
            this_search_string = 'nothing'
        else:
            this_search_string = '"' + self.search_string + '"'

        if self.zip_code_search == None:
            this_zip_code_search = 'empty zip code search'
        else:
            this_zip_code_search = 'zip code: "' + self.zip_code_search + '"'

        string = this_user + ' searched for: ' + this_search_string + ' and ' + this_zip_code_search
        return string

try:
    akismet.register(HobbyEvent)
except akismet.AlreadyModerated:
    pass

try:
    akismet.register(HobbyEventSignup)
except akismet.AlreadyModerated:
    pass

try:
    akismet.register(VisitHobbyEvent)
except akismet.AlreadyModerated:
    pass

try:
    akismet.register(EventSearch)
except akismet.AlreadyModerated:
    pass
