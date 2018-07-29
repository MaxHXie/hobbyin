from django.contrib import admin
from .models import HobbyEvent, HobbyEventSignup, VisitHobbyEvent, EventSearch

# Register your models here.
admin.site.register(HobbyEvent)
admin.site.register(HobbyEventSignup)
admin.site.register(VisitHobbyEvent)
admin.site.register(EventSearch)
