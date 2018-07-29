from .models import HobbyEvent, HobbyEventSignup
from django.forms import ModelForm
from django.db import models
from django.utils.safestring import mark_safe
from django import forms
from django.utils import timezone
from django.forms import TextInput, Select, Textarea, RadioSelect, CheckboxInput, NumberInput, CheckboxSelectMultiple, DateTimeInput
from django.core.files.images import get_image_dimensions
from django.utils.translation import gettext as _
from datetime import datetime
import re

class CreateEventForm(ModelForm):
    honeypot = forms.CharField(required=False,widget=forms.HiddenInput)
    datetime = forms.DateTimeField(
        widget = forms.DateTimeInput(
            attrs={'class': 'form-control', 'placeholder': 'Datum och tid på formatet: yyyy-mm-dd hh:mm', 'value': timezone.now().strftime("%Y-%m-%d %H:%M")}
        ),
        input_formats=[
            '%Y-%m-%d %H:%M',
            '%y-%m-%d %H:%M',
            '%Y/%m/%d %H:%M',
            '%y/%m/%d %H:%M',
            '%Y %m %d %H %M',
            '%y %m %d %H %M',
            '%Y-%m-%d %H:%M:%S',
            '%y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%y/%m/%d %H:%M:%S',
            '%Y %m %d %H %M %S',
            '%y %m %d %H %M %S',
        ],
        error_messages = {
            'required': 'Du måste fylla i en tid',
            'invalid': 'Du har angett fel format på tiden'
        },
    )
    class Meta:
        model = HobbyEvent
        fields = ['event_name', 'datetime', 'city', 'city_district', 'address', 'zip_code', 'location_name', 'price', 'description']
        widgets = {
            'event_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Namnet på evenemanget...'}),
            'city': TextInput(attrs={'class': 'form-control', 'placeholder': 'Stad... ex. Stockholm, Göteborg...'}),
            'city_district': TextInput(attrs={'class': 'form-control', 'placeholder': 'Kommun: ex. Sollentuna, Täby...'}),
            'zip_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Postnummer: ex. 123 45...'}),
            'address': TextInput(attrs={'class': 'form-control', 'placeholder': 'Address...'}),
            'location_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Namn på platsen (Om det finns något)...'}),
            'price': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Pris'}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Kort beskrivning om evenemanget', 'rows':20}),
        }
        error_messages = {
            'event_name': {
                'required': _('Du måste fylla i namnet på evenemanget'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'city': {
                'required': _('Du måste fylla i det vilken stad det är i'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'city_district': {
                'required': _('Du måste fylla i vilken kommun/stadsdel det är i'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'address': {
                'required': _('Du måste fylla i platsens adress'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'zip_code': {
                'required': _('Du måste fylla i platsens postnummer'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'location_name': {
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'price': {
                'required': _('Du måste fylla i priset på evenemanget. (Sätt 0 om det är gratis)'),
                'max_length': _('Texten du skrev in här var för långt'),
            },
            'description':{
                'max_length': _('Texten du skrev in här var för långt')
            }
        }

    def clean_event_name(self):
        event_name = self.cleaned_data['event_name']
        if event_name:
            if not re.match(r'^[a-zA-ZåäöÅÄÖØ1234567890 ]*$', event_name):
                raise forms.ValidationError(("Du har använt ogiltiga tecken i det här fältet"), code="invalid_event_name")
            else:
                return event_name

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
        if not re.match(r'^\d{3}(?:[-\s]\d{2})?(?:\d{2})?$', zip_code):
            raise forms.ValidationError(_("Du måste ange ett giltigt postnummer"), code="invalid_zip_code")
        else:
            return zip_code

    def clean_address(self):
        address = self.cleaned_data['address']
        if not re.match(r'^[a-zA-ZåäöÅÄÖØ1234567890 ]*$', address):
            raise forms.ValidationError(("Du har använt ogiltiga tecken i det här fältet"), code="invalid_address")
        else:
            return address

    def clean_location_name(self):
        location_name = self.cleaned_data['location_name']
        if location_name:
            if not re.match(r'^[a-zA-ZåäöÅÄÖØ1234567890 ]*$', location_name):
                raise forms.ValidationError(("Du har använt ogiltiga tecken i det här fältet"), code="invalid_location_name")
            else:
                return location_name
        else:
            return location_name

    def clean_honeypot(self):
        honeypot = self.cleaned_data['honeypot']
        if len(honeypot):
            raise forms.ValidationError()
        else:
            return honeypot
