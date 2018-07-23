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
    first_name = models.CharField(max_length=64, null=True, blank=False)
    last_name = models.CharField(max_length=64, null=True, blank=False)
    email = models.CharField(max_length=128, blank=True, null=True)
    telephone = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        try:
            string = self.first_name + " " + self.last_name + " to " + self.hobby_event.event_name
        except:
            string = "event_signup_name_error"
        return string

try:
    akismet.register(HobbyEvent)
except akismet.AlreadyModerated:
    pass

try:
    akismet.register(HobbyEventSignup)
except akismet.AlreadyModerated:
    pass
