from django.template.defaultfilters import register

@register.filter(name='lookup_dict')
def lookup_dict(dict, index):
    if index in dict:
        return dict[index]
    return ''
