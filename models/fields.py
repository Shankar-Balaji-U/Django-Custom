# Django imports
from django.db import connection
from django.db.models import Field
from django.forms.fields import CharField
from django.forms.widgets import NumberInput
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import (
            MaxLengthValidator, MinLengthValidator, 
            ProhibitNullCharactersValidator )
from django.utils.functional import cached_property

from .models.validators import VerhoeffValidator, GSTINValidator, PANValidator


class AadhaarField(Field):
    empty_strings_allowed = False
    default_error_messages = {
        'invalid': _('“%(value)s” is not a valid Aadhaar Number.'),
    }
    description = _('Unique Identification Authority of India')

    def __init__(self, verbose_name=None, **kwargs):
        kwargs['max_length'] = 12
        super().__init__(verbose_name, **kwargs)

    @cached_property
    def validators(self):
        # Just for readability
        validators_ = super().validators
        min_len, max_len = self.max_length, self.max_length
        validators_.append(VerhoeffValidator(message=self.error_messages['invalid']))
        return validators_

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError) as e:
            raise e.__class__(
                "Field '%s' expected a number but got %r." % (self.name, value),
            ) from e

    def to_python(self, value):
        if value is None:
            return value
        try:
            return str(value)
        except (TypeError, ValueError):
            raise ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': value},
            )

    def get_internal_type(self):
        return "IntegerField"

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        if self.null and not connection.features.interprets_empty_strings_as_nulls:
            defaults['empty_value'] = None
        defaults.update(kwargs)
        return super().formfield(**defaults)


class GSTField(Field):
    default_error_messages = {
        'invalid': _('“%(value)s” is not a valid GST Number.'),
    }
    description = _('Goods and Service Tax.')
    empty_strings_allowed = False

    def __init__(self, verbose_name=None, **kwargs):
        kwargs['max_length'] = 15
        super().__init__(verbose_name, **kwargs)

    @cached_property
    def validators(self):
        # Just for readability
        validators_ = super().validators
        min_length, max_length = self.max_length, self.max_length
        validators_.append(GSTINValidator(message=self.error_messages['invalid']))
        return validators_

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return None
        try:
            return str(value)
        except (TypeError, ValueError) as e:
            raise e.__class__(
                "Field '%s' expected a string but got %r." % (self.name, value),
            ) from e

    def to_python(self, value):
        if value is None:
            return value
        try:
            return str(value)
        except (TypeError, ValueError):
            raise ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': value},
            )

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super().formfield(**defaults)



class PANField(Field):
    default_error_messages = {
        'invalid': _('“%(value)s” is not a valid PAN Number.'),
    }
    description = _('Permanant Account Number.')
    empty_strings_allowed = False

    def __init__(self, verbose_name=None, **kwargs):
        kwargs['max_length'] = 15
        super().__init__(verbose_name, **kwargs)

    @cached_property
    def validators(self):
        # Just for readability
        validators_ = super().validators
        min_length, max_length = self.max_length, self.max_length
        validators_.append(PANValidator(message=self.error_messages['invalid']))
        return validators_

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return None
        try:
            return str(value)
        except (TypeError, ValueError) as e:
            raise e.__class__(
                "Field '%s' expected a string but got %r." % (self.name, value),
            ) from e

    def to_python(self, value):
        if value is None:
            return value
        try:
            return str(value)
        except (TypeError, ValueError):
            raise ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': value},
            )

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super().formfield(**defaults)
