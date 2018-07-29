from django.contrib import admin
from .models import Hobby, Instructor, Customer, InstructorMessage, VisitInstructor, InstructorSearch, Follower

admin.site.register(Hobby)
admin.site.register(Instructor)
admin.site.register(Customer)
admin.site.register(InstructorMessage)
admin.site.register(VisitInstructor)
admin.site.register(InstructorSearch)
admin.site.register(Follower)
