import json
import urllib
from django.conf import settings

from external_page.models import Instructor, Customer

def is_instructor(request):
    if request.user.is_authenticated:
        try:
            Instructor.objects.get(user=request.user)
            return True
        except Instructor.DoesNotExist:
            return False
    else:
        return False

def is_customer(request):
    if request.user.is_authenticated:
        try:
            Customer.objects.get(user=request.user)
            return True
        except Customer.DoesNotExist:
            return False
    else:
        return False

def get_profile_model(user):
    try:
        Instructor.objects.get(user=user)
        return Instructor
    except Instructor.DoesNotExist:
        pass

    try:
        Customer.objects.get(user=user)
        return Customer
    except Customer.DoesNotExist:
        pass

    return None

def sort_by_proximity(list_to_sort, input_zip_code, request):
    '''
    INPUT:
        list_to_sort        - A list of django model objects that have the attribute zip_code which is a string of numeric characters of 3-6 characters.
        input_zip_code      - A string or numeric characters of 3-6 characters.
        request             - A django http request object.

    RETURNS:
        worked              - A boolean. True if function ran without exceptions. False if function ran with exceptions.
        list_to_sort        - A list that is sorted, or none on failure.
        error               - A string of error message, or none on success.

    Sort list_to_sort according to how proximate its zip_code attribute is to input_zip_code. Proximity is defined in this function
    '''

    def sort_zip_code1(obj, area_code):
        if obj.zip_code != None:
            try:
                return abs(area_code1 - int(obj.zip_code[0] + obj.zip_code[1]))
            except:
                return 1000
        else:
            return 1000

    def sort_zip_code2(obj, area_code):
        if obj.zip_code != None:
            try:
                return abs(area_code2 - int(obj.zip_code[2]))
            except:
                return 1000
        else:
            return 1000

    area_code1 = None
    area_code2 = None
    worked = True
    error = None

    if input_zip_code != "" and input_zip_code != None:
        try:
            area_code1 = int(input_zip_code[0] + input_zip_code[1])
            area_code2 = int(input_zip_code[2])
        except:
            worked = False
            error = 'Vi kunde inte göra en sökning med det där postnumret.'

    elif is_instructor(request):
        try:
            area_code1 = int(request.user.instructor.zip_code[0] + request.user.instructor.zip_code[1])
            area_code2 = int(request.user.instructor.zip_code[2])
        except:
            worked = False

    elif is_customer(request):
        try:
            area_code1 = int(request.user.customer.zip_code[0] + request.user.customer.zip_code[1])
            area_code2 = int(request.user.customer.zip_code[2])
        except:
            worked = False

    if area_code1 != None and area_code2 != None:
        try:
            list_to_sort.sort(key=lambda x: (sort_zip_code1(x, area_code1), sort_zip_code2(x, area_code2)))
        except:
            worked = False
            list_to_sort = None
            error = 'Något gick fel, vi kunde inte sortera evenemangen på avstånd. Dubbelkolla ditt postnummer.'

    return worked, list_to_sort, error



def check_user_valid_profile(request):
    current_user = request.user
    if is_instructor(request):
        try:
            instructor = Instructor.objects.get(user=current_user)
            if instructor.valid_profile:
                if instructor.is_active:
                    return 'success'
                else:
                    return 'not_active'
            else:
                return 'not_valid'
        except Instructor.DoesNotExist:
            create_instructor(current_user)
            return False

    elif is_customer(request):
        try:
            customer = Customer.objects.get(user=current_user)
            if customer.valid_profile:
                if customer.is_active:
                    return 'success'
                else:
                    return 'not_active'
            else:
                return 'not_valid'
        except Customer.DoesNotExist:
            create_customer(current_user)
            return False


def create_instructor(current_user):
    instructor = Instructor.objects.create(user=current_user)
    instructor.save()
    return instructor


def create_customer(current_user):
    customer = Customer.objects.create(user=current_user)
    customer.save()
    return customer

def compose_message(message_object):
    if message_object.email == None:
        email = ""
    else:
        email = "Email: " + message_object.email + " \n"

    if message_object.telephone == None:
        telephone = ""
    else:
        telephone = "Telefon: " + message_object.telephone + "\n"

    if message_object.message == None:
        message_text = ""
    else:
        message_text = "[MEDDELANDE]" + " \n\n" + message_object.message + " \n\n"

    subject =   "[Hobbyin] Du har fått en kundförfrågan!"
    message =   ["[KUNDINFORMATION]" + " \n\n",
                "Namn: " + message_object.first_name + " \n",
                email,
                telephone,
                " \n\n",
                message_text,
                "Med vänlig hälsning" + " \n\n",
                message_object.first_name]

    message = "".join(message)
    return subject, message

def get_this_user(request):
    if request.user.is_authenticated:
        this_user = request.user
    else:
        this_user = None

    return this_user

def google_recaptcha(request):
    #Begin reCAPTCHA validation
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
    'secret': getattr(settings, "GOOGLE_RECAPTCHA_SECRET_KEY", None),
    'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req =  urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    return result
    #End reCAPTCHA validation
