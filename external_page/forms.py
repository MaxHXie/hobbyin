from external_page.models import Instructor, Customer, Hobby, InstructorMessage
from django.forms import ModelForm
from django.db import models
from django.utils.safestring import mark_safe
from django import forms
from allauth.account.forms import SignupForm
from django.forms import TextInput, Select, Textarea, RadioSelect, CheckboxInput, NumberInput, CheckboxSelectMultiple
from django.core.files.images import get_image_dimensions
from django.utils.translation import gettext as _
import hobbyin.functions as functions
import re

class CheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, *args, **kwargs):
        output = super(CheckboxSelectMultiple, self).render(*args, **kwargs)
        output = output.replace(u'<li>', u'')
        output = output.replace(u'</li>', u'')
        return mark_safe(output.replace(u'<ul id="id_hobbies">', u''))

class InstructorSignUpForm(SignupForm):
    def save(self, request):
        user = super(InstructorSignUpForm, self).save(request)
        user.save()
        functions.create_instructor(user, email=user.email)
        return user

class CustomerSignUpForm(SignupForm):
    def save(self, request):
        user = super(CustomerSignUpForm, self).save(request)
        user.save()
        functions.create_customer(user, email=user.email)
        return user

class InstructorForm(ModelForm):
    honeypot = forms.CharField(required=False,widget=forms.HiddenInput)
    class Meta:
        model = Instructor
        fields = ['hobbies', 'profile_picture', 'first_name', 'last_name', 'city', 'city_district', 'zip_code', 'description', 'is_private_instructor', 'work_in_student_home', 'work_in_instructor_home', 'maximum_students', 'price', 'price_model']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Förnamn'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Efternamn'}),
            'hobbies': RadioSelect(),
            'city': TextInput(attrs={'class': 'form-control', 'placeholder': 'Stad... ex. Stockholm, Göteborg...'}),
            'city_district': TextInput(attrs={'class': 'form-control', 'placeholder': 'Kommun: ex. Sollentuna, Täby...'}),
            'zip_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Postnummer: ex. 123 45...'}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Kort biografi om dig själv: Hej...', 'rows':20}),
            'is_private_instructor': CheckboxInput(attrs={'class': 'bootstrap-switch', 'data-on-label': 'JA', 'data-off-label': 'NEJ', 'onchange': 'hide_show_instructor_fields()'}),
            'work_in_student_home': CheckboxInput(),
            'work_in_instructor_home': CheckboxInput(),
            'maximum_students': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Antal personer jag klan lära ut till per tillfälle'}),
            'price': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Pris per timme'}),
            'price_model': RadioSelect(),
        }
        error_messages = {
            'first_name': {
                'required': _('Du måste fylla i ditt förnamn'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'last_name': {
                'required': _('Du måste fylla i ditt efternamn'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'hobbies': {
                'required': _('Du måste välja en hobby'),
            },
            'city': {
                'required': _('Du måste fylla i din stad'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'city_district': {
                'required': _('Du måste fylla i din kommun/stadsdel'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'zip_code': {
                'required': _('Du måste fylla i ditt postnummer'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'description': {
                'max_length': _('Texten du skrev in här var för långt, max 2500 tecken'),
            },
            'work_in_student_home': {
            },
            'work_in_instructor_home': {
            },
            'maximum_students': {
                'required': _('Du måste fylla i hur många hobbyister du kan ta per gång'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
        }

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', first_name):
            raise forms.ValidationError(("Du har använt ogiltiga tecken i det här fältet"), code="invalid_first_name")
        else:
            return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', last_name):
            raise forms.ValidationError(("Du har använt ogiltiga tecken i det här fältet"), code="invalid_last_name")
        else:
            return last_name

    def clean_city(self):
        city = self.cleaned_data['city']
        if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', city):
            raise forms.ValidationError(("Du har använt ogiltiga tecken i det här fältet"), code="invalid_city")
        else:
            return city

    def clean_city_district(self):
        city_district = self.cleaned_data['city_district']
        if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', city_district):
            raise forms.ValidationError(("Du har använt ogiltiga tecken i det här fältet"), code="invalid_city_district")
        else:
            return city_district

    def clean_zip_code(self):
        zip_code = self.cleaned_data['zip_code']
        if not re.match(r'^(\d{5}|\d{3}[\s]\d{2}|\d{3}-\d{2})$', zip_code):
            raise forms.ValidationError(_("Du måste ange ett giltigt postnummer"), code="invalid_zip_code")
        else:
            return zip_code

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



class CustomerForm(ModelForm):
    honeypot = forms.CharField(required=False,widget=forms.HiddenInput)
    class Meta:
        model = Customer
        fields = ['profile_picture', 'first_name', 'last_name', 'telephone', 'zip_code']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Förnamn'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Efternamn'}),
            'telephone': TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefonnummer'}),
            'zip_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Postnummer: ex. 123 45...'}),
        }
        error_messages = {
            'first_name': {
                'required': _('Du måste fylla i ditt förnamn'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'last_name': {
                'required': _('Du måste fylla i ditt efternamn'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'telephone': {
                'required': _('Du måste fylla i ett telefonnummer'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'zip_code': {
                'required': _('Du måste fylla i ditt postnummer'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
        }

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', first_name):
            raise forms.ValidationError(_("Du har använt ogiltiga tecken i det här fältet"), code="invalid_first_name")
        else:
            return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not re.match(r'^[a-zA-ZåäöÅÄÖØ ]*$', last_name):
            raise forms.ValidationError(_("Du har använt ogiltiga tecken i det här fältet"), code="invalid_last_name")
        else:
            return last_name

    def clean_telephone(self):
        telephone = self.cleaned_data['telephone']
        mobile_regex = r'^(\+46|0|\(\+46\)) *(7[0236])( |-|)(\d{4} \d{3}|\d{3} \d{4}|\d{3} \d{2} \d{2}|\d{2} \d{2} \d{3}|\d{7})$'
        home_phone_regex = r'^(\+46|0|\(\+46\)) *(8)( |-|)(\d{4} \d{2}|\d{2} \d{4}|\d{3} \d{3}|\d{2} \d{2} \d{2}|\d{6})$'
        if re.match(mobile_regex, telephone) or re.match(home_phone_regex, telephone):
            return telephone
        else:
            raise forms.ValidationError(_("Du måste ange ett giltigt telefonnummer"), code="invalid_telephone")

    def clean_zip_code(self):
        zip_code = self.cleaned_data['zip_code']
        if not re.match(r'^(\d{5}|\d{3}[\s]\d{2}|\d{3}-\d{2})$', zip_code):
            raise forms.ValidationError(_("Du måste ange ett giltigt postnummer"), code="invalid_zip_code")
        else:
            return zip_code

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
