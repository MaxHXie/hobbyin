from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Hobby(models.Model):
    hobby_name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.hobby_name

class Instructor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(max_length=64, null=True, blank=False)
    last_name = models.CharField(max_length=64, null=True, blank=False)
    hobbies = models.ManyToManyField(Hobby, null=True, blank=False)
    email = models.EmailField(max_length=256, blank=True, null=True, unique=True)
    city = models.CharField(max_length=128, null=True, blank=False)
    zip_code = models.CharField(max_length=10, null=True, blank=False)
    description = models.TextField(max_length=2048, null=True, blank=True)
    gender = models.CharField(max_length=1,
                           choices=(
                                    ('M', 'Male'),
                                    ('F', 'Female'),
                                    ('O', 'Other')
                           ), null=True
                           )
    work_in_student_home = models.BooleanField(default=False)
    work_in_instructor_home = models.BooleanField(default=True)
    maximum_students = models.PositiveIntegerField(default=2)

    def __str__(self):
        try:
            string = self.first_name + " " + self.last_name
        except:
            string = "name_error"
        return string

class Grade(models.Model):
    pass
    # Connect (instructor-hobby) to user grade of that (instructor-hobby) combination
