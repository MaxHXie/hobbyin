from django.contrib import admin
from .models import Hobby, Instructor, InstructorMessage

admin.site.register(Hobby)
admin.site.register(Instructor)
admin.site.register(InstructorMessage)
