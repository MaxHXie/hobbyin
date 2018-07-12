from external_page.models import Instructor
from django.forms import ModelForm
from django.forms import TextInput, Select, Textarea, RadioSelect, CheckboxInput, NumberInput

class InstructorForm(ModelForm):
    class Meta:
        model = Instructor
        fields = ['first_name', 'last_name', 'hobbies', 'city', 'zip_code', 'description', 'gender', 'work_in_student_home', 'work_in_instructor_home', 'maximum_students']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Förnamn'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Efternamn'}),
            'hobbies': Select(attrs={'class': 'form-control', 'placeholder': 'Jag vill instruera i: '}),
            'city': TextInput(attrs={'class': 'form-control', 'placeholder': 'Stad'}),
            'zip_code': TextInput(attrs={'class': 'form-control', 'placeholder': 'Postkod'}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Kort biografi'}),
            'gender': RadioSelect(attrs={'class': 'form-control', 'placeholder': 'Kön'}),
            'work_in_student_home': CheckboxInput(),
            'work_in_instructor_home': CheckboxInput(),
            'maximum_students': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Antal hobbyister jag kan ta upp till'}),
        }
