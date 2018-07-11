from django.shortcuts import render
from external_page.models import Hobby, Instructor

# Create your views here.
def index(request):
    hobbies = Hobby.objects.all()
    if len(hobbies)==0:
        hobbies = None
    return render(request, 'landing_page.html', context={'hobbies': hobbies})

def instructors(request, hobby_name):
    if hobby_name == "malning":
        hobby_name = "målning"
    try:
        hobby = Hobby.objects.get(hobby_name=hobby_name)
        instructors = hobby.instructor_set.all()
    except Hobby.DoesNotExist:
        hobby = None
        instructors = []

    return render(request, 'instructors_page.html', context={'hobby': hobby, 'hobby_name': hobby_name, 'instructors': instructors})

def profile(request, instructor_id):
    instructor = Instructor.objects.get(pk=instructor_id)
    return render(request, 'profile_page.html', context={'instructor':instructor})
