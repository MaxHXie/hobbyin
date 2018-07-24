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

    elif request.user.is_authenticated and request.user.instructor:
        try:
            area_code1 = int(request.user.instructor.zip_code[0] + request.user.instructor.zip_code[1])
            area_code2 = int(request.user.instructor.zip_code[2])
        except:
            worked = False

    elif request.user.is_authenticated and request.user.customer:
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
