from external_page.models import Instructor, Hobby, Message
from django.forms import ModelForm
from django.db import models
from django.utils.safestring import mark_safe
from django import forms
from django.forms import TextInput, Select, Textarea, RadioSelect, CheckboxInput, NumberInput, CheckboxSelectMultiple
from django.core.files.images import get_image_dimensions
from django.utils.translation import gettext as _
import re

class CheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, *args, **kwargs):
        output = super(CheckboxSelectMultiple, self).render(*args, **kwargs)
        output = output.replace(u'<li>', u'')
        output = output.replace(u'</li>', u'')
        return mark_safe(output.replace(u'<ul id="id_hobbies">', u''))

class InstructorForm(ModelForm):
    class Meta:
        model = Instructor
        fields = ['profile_picture', 'first_name', 'last_name', 'city', 'zip_code', 'work_in_student_home', 'work_in_instructor_home', 'hobbies', 'maximum_students', 'price', 'price_model', 'description']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Förnamn'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Efternamn'}),
            'hobbies': RadioSelect(),
            'city': TextInput(attrs={'class': 'form-control', 'placeholder': 'Stad: Stockholm'}),
            'zip_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Postnummer: 123 45'}),
            'work_in_student_home': CheckboxInput(),
            'work_in_instructor_home': CheckboxInput(),
            'maximum_students': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Antal personer jag klan lära ut till per tillfälle'}),
            'price': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Pris per timme'}),
            'price_model': RadioSelect(),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Kort biografi om dig själv: Hej jag heter...', 'rows':20}),
        }
        error_messages = {
            'first_name': {
                'required': _('Du måste fylla i det här fältet!'),
                'max_length': _('Texten du skrev in här var för långt!'),
            },
            'last_name': {
                'required': _('Du måste fylla i det här fältet!'),
                'max_length': _('Texten du skrev in här var för långt!'),
            },
            'hobbies': {
                'required': _('Du måste välja en hobby!'),
            },
            'city': {
                'required': _('Du måste fylla i det här fältet!'),
                'max_length': _('Texten du skrev in här var för långt!'),
            },
            'zip_code': {
                'required': _('Du måste fylla i det här fältet!'),
                'max_length': _('Texten du skrev in här var för långt!'),
            },
            'description': {
                'max_length': _('Texten du skrev in här var för långt!'),
            },
            'work_in_student_home': {
            },
            'work_in_instructor_home': {
            },
            'maximum_students': {
                'required': _('Du måste fylla i det här fältet!'),
                'max_length': _('Texten du skrev in här var för långt!'),
            },
        }

    def clean(self):
        cleaned_data=super(InstructorForm, self).clean()

        first_name = cleaned_data.get('first_name')
        if first_name:
            print(first_name)
            if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', first_name):
                raise forms.ValidationError({'first_name':[_("Du har använt ogiltiga tecken i det här fältet")]}, code="invalid_first_name")

        last_name = cleaned_data.get('last_name')
        if last_name:
            if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', last_name):
                raise forms.ValidationError({'last_name':[_("Du har använt ogiltiga tecken i det här fältet")]}, code="invalid_last_name")

        zip_code = cleaned_data.get('zip_code')
        if not re.match(r'^\d{3}(?:[-\s]\d{2})?(?:\d{2})?$', zip_code):
            raise forms.ValidationError({'zip_code':[_("Du måste ange ett giltigt postnummer")]}, code="invalid_zip_code")

        work_in_student_home = cleaned_data.get('work_in_student_home')
        work_in_instructor_home = cleaned_data.get('work_in_instructor_home')
        if work_in_instructor_home == False and work_in_student_home == False:
            raise forms.ValidationError({'work_in_student_home':[_("Du måste välja hur du vill lära ut.")]}, code="choose_one")

    def clean_profile_picture(self):
        try:
            profile_picture = self.cleaned_data['profile_picture']

            try:
                w, h = get_image_dimensions(profile_picture)

                #validate dimensions
                max_width = 1000
                max_height = 1000
                if w > max_width or h > max_height:
                    raise forms.ValidationError(_('Din profilbild får inte vara större än %s pixlar på höjden eller %s på bredden') % (max_width, max_height))

                #validate content type
                main, sub = profile_picture.content_type.split('/')
                if not (main == 'image' and sub in ['jpeg', 'jpg', 'png']):
                    raise forms.ValidationError(_('Du måste ladda upp en .jpg eller .png fil.'))

                #validate file size
                if len(profile_picture) > (1000 * 1024):
                    raise forms.ValidationError(_('profile_picture file size may not exceed 1 Megabyte.'))

            except AttributeError:
                """
                Handles case when we are updating the user profile
                and do not supply a new profile_picture
                """
                pass

            return profile_picture

        except:
            pass


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

        error_messages = {
            'first_name': {
                'required': _('Du måste fylla i det här fältet!'),
                'max_length': _('Texten du skrev in här var för långt!'),
            },
        }

    def clean(self):
        cleaned_data=super(ContactInstructorForm, self).clean()

        first_name
        zip_code = cleaned_data.get('zip_code')
        if not re.match(r'^\d{3}(?:[-\s]\d{2})?(?:\d{2})?$', zip_code):
            raise forms.ValidationError({'zip_code':[_("Du måste ange ett giltigt postnummer!")]}, code="invalid")
