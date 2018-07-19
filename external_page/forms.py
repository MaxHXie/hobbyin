from external_page.models import Instructor, Hobby, InstructorMessage
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
    honeypot = forms.CharField(required=False,widget=forms.HiddenInput)
    class Meta:
        model = Instructor
        fields = ['profile_picture', 'first_name', 'last_name', 'city', 'city_district', 'zip_code', 'work_in_student_home', 'work_in_instructor_home', 'hobbies', 'maximum_students', 'price', 'price_model', 'description']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Förnamn'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Efternamn'}),
            'hobbies': RadioSelect(),
            'city': TextInput(attrs={'class': 'form-control', 'placeholder': 'Stad... ex. Stockholm, Göteborg...'}),
            'city_district': TextInput(attrs={'class': 'form-control', 'placeholder': 'Kommun: ex. Sollentuna, Täby...'}),
            'zip_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Postnummer: ex. 123 45...'}),
            'work_in_student_home': CheckboxInput(),
            'work_in_instructor_home': CheckboxInput(),
            'maximum_students': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Antal personer jag klan lära ut till per tillfälle'}),
            'price': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Pris per timme'}),
            'price_model': RadioSelect(),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Kort biografi om dig själv: Hej jag heter...', 'rows':20}),
        }
        error_messages = {
            'first_name': {
                'required': _('Du måste fylla i det här fältet'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'last_name': {
                'required': _('Du måste fylla i det här fältet'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'hobbies': {
                'required': _('Du måste välja en hobby'),
            },
            'city': {
                'required': _('Du måste fylla i det här fältet'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'city_district': {
                'required': _('Du måste fylla i det här fältet'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'zip_code': {
                'required': _('Du måste fylla i det här fältet'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'description': {
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'work_in_student_home': {
            },
            'work_in_instructor_home': {
            },
            'maximum_students': {
                'required': _('Du måste fylla i det här fältet'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
        }

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if first_name:
            if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', first_name):
                raise forms.ValidationError(("Du har använt ogiltiga tecken i det här fältet"), code="invalid_first_name")

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if last_name:
            if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', last_name):
                raise forms.ValidationError(("Du har använt ogiltiga tecken i det här fältet"), code="invalid_last_name")

    def clean_zip_code(self):
        zip_code = self.cleaned_data['zip_code']
        if not re.match(r'^\d{3}(?:[-\s]\d{2})?(?:\d{2})?$', zip_code):
            raise forms.ValidationError(_("Du måste ange ett giltigt postnummer"), code="invalid_zip_code")

    def clean_profile_picture(self):
        try:
            profile_picture = self.cleaned_data['profile_picture']

            try:
                w, h = get_image_dimensions(profile_picture)

                #validate dimensions
                max_width = 1080
                max_height = 1080
                if w > max_width or h > max_height:
                    raise forms.ValidationError(_('Din profilbild får inte vara större än pixlar på höjden eller %s på bredden') % (max_width, max_height))

                #validate content type
                main, sub = profile_picture.content_type.split('/')
                if not (main == 'image' and sub in ['jpeg', 'jpg', 'png']):
                    raise forms.ValidationError(_('Du måste ladda upp en .jpg eller .png fil.'))

                #validate file size
                if len(profile_picture) > (1000 * 1024):
                    raise forms.ValidationError(_('Din profilbild får inte vara större än 1 Megabyte i storlek.'))

            except AttributeError:
                """
                Handles case when we are updating the user profile
                and do not supply a new profile_picture
                """
                pass

            return profile_picture

        except:
            pass

    def clean_honeypot(self):
        honeypot = self.cleaned_data['honeypot']
        if len(honeypot):
            raise forms.ValidationError()
        else:
            return honeypot

    def clean(self):
        cleaned_data=super(InstructorForm, self).clean()

        work_in_student_home = self.cleaned_data['work_in_student_home']
        work_in_instructor_home = self.cleaned_data['work_in_instructor_home']
        if work_in_instructor_home == False and work_in_student_home == False:
            raise forms.ValidationError({'work_in_student_home':[_("Du måste välja hur du vill lära ut.")]}, code="choose_one")

class ContactInstructorForm(ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)
    class Meta:
        model = InstructorMessage
        fields = ['first_name', 'email', 'telephone', 'message']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Förnamn'}),
            'email': TextInput(attrs={'class': 'form-control', 'placeholder': 'Email adress'}),
            'telephone': TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefonnummer'}),
            'message': Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':80, 'placeholder':'Skriv in ditt meddelande här'}),
        }

        error_messages = {
            'first_name': {
                'required': _('Du måste fylla i det här fältet'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'email':{
                'max_length': _('Din email du skrev in här är för långt'),
            },
            'message': {
                'required': _('Du måste fylla i det här fältet'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
        }

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if first_name:
            if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', first_name.strip()):
                raise forms.ValidationError(_("Du har använt ogiltiga tecken i det här fältet"), code="invalid_first_name")
            else:
                return first_name
        else:
            raise forms.ValidationError(_('Du måste fylla i det här fältet'), code="empty_first_name")

    def clean_honeypot(self):
        honeypot = self.cleaned_data['honeypot']
        if len(honeypot):
            raise forms.ValidationError()
        else:
            return honeypot

    def clean_email(self):
        email = self.cleaned_data['email']
        email_regex = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
        if re.match(email_regex, email):
            return email

    def clean_telephone(self):
        telephone = self.cleaned_data['telephone']
        mobile_regex = r'^(\+46|0|\(\+46\)) *(7[0236])( |-|)(\d{4} \d{3}|\d{3} \d{4}|\d{3} \d{2} \d{2}|\d{2} \d{2} \d{3}|\d{7})$'
        home_phone_regex = r'^(\+46|0|\(\+46\)) *(8)( |-|)(\d{4} \d{2}|\d{2} \d{4}|\d{3} \d{3}|\d{2} \d{2} \d{2}|\d{6})$'
        if re.match(mobile_regex, telephone) or re.match(home_phone_regex, telephone):
            return telephone

    def clean(self):
        cleaned_data=super(ContactInstructorForm, self).clean()

        email = self.cleaned_data['email']
        telephone = self.cleaned_data['telephone']

        if email == None and telephone == None:
            raise forms.ValidationError({'email': [_('Du måste skriva in en giltig email eller ett giltigt telefonnummer')]}, code="invalid_email_and_phone")
