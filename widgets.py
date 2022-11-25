from django.forms.widgets import Input


class SearchInput(Input):
    input_type = 'search'

class PhoneInput(Input):
    input_type = 'tel'
