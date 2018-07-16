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
    hobbies = models.ManyToManyField(Hobby, blank=False)
    email = models.EmailField(max_length=128, blank=True, null=True, unique=True)
    city = models.CharField(max_length=64, null=True, blank=False)
    zip_code = models.CharField(max_length=6, null=True, blank=False)
    description = models.TextField(max_length=2048, null=True, blank=True)
    gender = models.CharField(max_length=1,
                           choices=(
                                    ('N', 'No answer'),
                                    ('M', 'Male'),
                                    ('F', 'Female'),
                                    ('O', 'Other')
                           ), null=True, blank=True, default="N"
                           )
    work_in_student_home = models.BooleanField(default=False)
    work_in_instructor_home = models.BooleanField(default=True)
    maximum_students = models.PositiveIntegerField(default=1, blank=False)

    def __str__(self):
        try:
            string = self.first_name + " " + self.last_name
        except:
            string = "name_error"
        return string

class Message(models.Model):
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(max_length=64, null=False)
    email = models.EmailField(max_length=128, null=False)
    telephone = models.CharField(max_length=32, null=False)
    message = models.CharField(max_length=2048, null=False)

    def __str__(self):
        try:
            string = self.first_name + " to " + self.to_user.email
        except:
            string = "message_name_error"
        return string
