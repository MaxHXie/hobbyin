from external_page.models import Instructor, Hobby, Message
from django.forms import ModelForm
from django.db import models
from django.utils.safestring import mark_safe
from django import forms
from django.forms import TextInput, Select, Textarea, RadioSelect, CheckboxInput, NumberInput, CheckboxSelectMultiple

class CheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, *args, **kwargs):
        output = super(CheckboxSelectMultiple, self).render(*args, **kwargs)
        output = output.replace(u'<li>', u'')
        output = output.replace(u'</li>', u'')
        return mark_safe(output.replace(u'<ul id="id_hobbies">', u''))

class InstructorForm(ModelForm):
    class Meta:
        model = Instructor
        fields = ['first_name', 'last_name', 'city', 'zip_code', 'work_in_student_home', 'work_in_instructor_home', 'hobbies', 'maximum_students', 'description']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Förnamn'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Efternamn'}),
            'hobbies': CheckboxSelectMultiple(),
            'city': TextInput(attrs={'class': 'form-control', 'placeholder': 'Stad'}),
            'zip_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Postnummer'}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Kort biografi om dig själv', 'rows':20}),
            'work_in_student_home': CheckboxInput(),
            'work_in_instructor_home': CheckboxInput(),
            'maximum_students': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Antal hobbyister jag kan ta upp till'}),
        }

class ContactInstructorForm(ModelForm):
    class Meta:
        model = Message
        fields = ['first_name', 'email', 'telephone', 'message']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Förnamn'}),
            'email': TextInput(attrs={'class': 'form-control', 'placeholder': 'Email adress'}),
            'telephone': TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon-nummer'}),
            'message': Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':80, 'placeholder':'Skriv in ditt meddelande här'}),
        }
