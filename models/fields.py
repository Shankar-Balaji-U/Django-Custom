# Django imports
from django.db import connection
from django.db import models
from django import forms
from django.forms.widgets import NumberInput
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import (
            MaxLengthValidator, MinLengthValidator, 
            ProhibitNullCharactersValidator )
from django.utils.functional import cached_property
from django.db import connection
from django.utils import timezone

from .models.validators import VerhoeffValidator, GSTINValidator, PANValidator


class AadhaarField(models.Field):
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


class GSTField(models.Field):
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
        return "GSTField"

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super().formfield(**defaults)



class PANField(models.Field):
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
        return "PANField"

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super().formfield(**defaults)



class SerialNumberField(models.CharField):
	prefix = None

	def __init__(self, *args, **kwargs):
		self.prefix = kwargs.pop('prefix', None)
		kwargs.setdefault('max_length', 20)
		kwargs.setdefault('editable', False)
		super().__init__(*args, **kwargs)

	def deconstruct(self):
		name, path, args, kwargs = super().deconstruct()
		del kwargs['max_length']
		del kwargs['editable']
		return name, path, args, kwargs

	def get_internal_type(self):
		return "SerialNumberField"

	def formfield(self, **kwargs):
		defaults = super().formfield(**{
			"initial": self.get_serial_number(), 
			**kwargs
		})
		return defaults

	def _check_to_reset(self):
		with connection.cursor() as cursor:
			cursor.execute("SELECT created_date FROM serialnumber_sequence WHERE tb_name = %s;", [self.tb_name])
			(created_date,) = cursor.fetchone()
		today_date = timezone.localtime().date()
 
		# Set the counter value to 0; Set the date to today_date
		return today_date > created_date

	def get_serial_number(self):
		count, date = self.get_next_value()
		return f"#{self.prefix}{date.strftime('%Y%m%d')}-{count:03d}"

	def get_next_value(self):
		# Retrieve the next value of the sequence for a given table name
		with connection.cursor() as cursor:
			if self._check_to_reset():
				self._reset_count()
			
			cursor.execute("SELECT seq, created_date FROM serialnumber_sequence WHERE tb_name = %s;", [self.tb_name])
			(seq, created_date) = cursor.fetchone()

			return seq, created_date

	def _reset_count(self):
		with connection.cursor() as cursor:
			cursor.execute(
				"UPDATE serialnumber_sequence SET seq = 0, created_date = %s WHERE tb_name = %s;", 
				[timezone.localtime().date(), self.tb_name]
			)

	def _increment_count(self):
		# Update the next value of the sequence for a given table name
		with connection.cursor() as cursor:
			cursor.execute(
				"UPDATE serialnumber_sequence SET seq = seq + 1 WHERE tb_name = %s;", 
				[self.tb_name]
			)

	def contribute_to_class(self, cls, name, **kwargs):
		super().contribute_to_class(cls, name, **kwargs)
		self.tb_name = f'{cls._meta.db_table}_{cls._meta.app_label}'

		# When a model has this field then it will create a table classed `serialnumber_sequence`
		with connection.cursor() as cursor:
			cursor.execute("""
				CREATE TABLE IF NOT EXISTS serialnumber_sequence (
					tb_name VARCHAR(100) PRIMARY KEY, 
					seq BIGINT UNSIGNED, 
					created_date DATE
				)
			""")

			cursor.execute(
				'INSERT OR IGNORE INTO serialnumber_sequence VALUES (%s, 0, %s);', 
				(self.tb_name, timezone.localtime().date())
			)

	def pre_save(self, model_instance, add):
		if add:
			if self._check_to_reset():
				self._reset_count()

			if not getattr(model_instance, self.attname):
				setattr(model_instance, self.attname, self.get_serial_number())
			self._increment_count()

		return super().pre_save(model_instance, add)

