from django.contrib import admin
from .models import HobbyEvent, HobbyEventSignup

# Register your models here.
admin.site.register(HobbyEvent)
admin.site.register(HobbyEventSignup)
