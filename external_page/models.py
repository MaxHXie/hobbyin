from django.db import models
from django.contrib.auth.models import User
from djangospam.akismet import moderator as akismet
from datetime import datetime

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
    hobbies = models.ForeignKey(Hobby, on_delete=models.CASCADE, blank=False, null=True)
    email = models.EmailField(max_length=128, blank=True, null=True, unique=True)
    city = models.CharField(max_length=64, null=True, blank=False)
    city_district = models.CharField(max_length=64, null=True, blank=False)
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
    price = models.PositiveIntegerField(default=300, blank=False)
    price_model = models.CharField(max_length=1,
                           choices=(
                                    ('H', 'per timme'),
                                    ('X', 'per timme och per person'),
                                    ('T', 'per tillfälle'),
                                    ('Y', 'per tillfälle och per person'),
                           ), null=True, blank=False, default="H"
                           )
    profile_picture = models.ImageField(upload_to="profile_picture", blank=True, null=True)
    valid_profile = models.BooleanField(default=False)

    def __str__(self):
        try:
            string = self.first_name + " " + self.last_name
        except:
            string = "name_error"
        return string

class InstructorMessage(models.Model):
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(max_length=64, null=True, blank=False)
    email = models.CharField(max_length=128, blank=True, null=True)
    telephone = models.CharField(max_length=32, blank=True, null=True)
    message = models.CharField(max_length=2048, null=True, blank=True)
    message_sent = models.BooleanField(default=False)
    time_now = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        try:
            string = self.first_name + " to " + self.to_user.email
        except:
            string = "message_name_error"
        return string

class Customer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(max_length=64, null=True, blank=False)
    last_name = models.CharField(max_length=64, null=True, blank=False)
    email = models.EmailField(max_length=128, blank=True, null=True, unique=True)
    city = models.CharField(max_length=64, null=True, blank=False)
    city_district = models.CharField(max_length=64, null=True, blank=False)
    zip_code = models.CharField(max_length=6, null=True, blank=False)
    gender = models.CharField(max_length=1,
                           choices=(
                                    ('N', 'No answer'),
                                    ('M', 'Male'),
                                    ('F', 'Female'),
                                    ('O', 'Other')
                           ), null=True, blank=True, default="N"
                           )
    profile_picture = models.ImageField(upload_to="profile_picture", blank=True, null=True)

    def __str__(self):
        try:
            string = self.first_name + " " + self.last_name
        except:
            string = "name_error"
        return string



try:
    akismet.register(Instructor)
except akismet.AlreadyModerated:
    pass

try:
    akismet.register(Customer)
except akismet.AlreadyModerated:
    pass

try:
    akismet.register(InstructorMessage)
except akismet.AlreadyModerated:
    pass
