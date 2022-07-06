from django.db.models import Field
from django.forms.fields import CharField
from django.forms.widgets import NumberInput
from django.utils.translation import gettext_lazy as _
from django.core import checks, exceptions, validators
from django.db import connection, connections, router

	#     'AutoField': 'integer'
	#     'BigAutoField': 'integer'
	#     'BinaryField': 'BLOB'
	#     'BooleanField': 'bool'
	#     'CharField': 'varchar(%(max_length)s)'
	#     'DateField': 'date'
	#     'DateTimeField': 'datetime'
	#     'DecimalField': 'decimal'
	#     'DurationField': 'bigint'
	#     'FileField': 'varchar(%(max_length)s)'
	#     'FilePathField': 'varchar(%(max_length)s)'
	#     'FloatField': 'real'
	#     'IntegerField': 'integer'
	#     'BigIntegerField': 'bigint'
	#     'IPAddressField': 'char(15)'
	#     'GenericIPAddressField': 'char(39)'
	#     'JSONField': 'text'
	#     'NullBooleanField': 'bool'
	#     'OneToOneField': 'integer'
	#     'PositiveBigIntegerField': 'bigint unsigned'
	#     'PositiveIntegerField': 'integer unsigned'
	#     'PositiveSmallIntegerField': 'smallint unsigned'
	#     'SlugField': 'varchar(%(max_length)s)'
	#     'SmallAutoField': 'integer'
	#     'SmallIntegerField': 'smallint'
	#     'TextField': 'text'
	#     'TimeField': 'time'
	#     'UUIDField': 'char(32)'






class UIDAIField(Field):
	default_error_messages = {
		'invalid': _('“%(value)s” is not a valid Aadhaar Number.'),
	}
	description = _('Unique Identification Authority of India')
	empty_strings_allowed = False

	def __init__(self, verbose_name=None, **kwargs):
		kwargs['max_length'] = 12
		super().__init__(verbose_name, **kwargs)

	def deconstruct(self):
		name, path, args, kwargs = super().deconstruct()
		del kwargs['max_length']
		return name, path, args, kwargs

	def to_python(self, value):
		"""Return a integer."""
		if value not in self.empty_values:
			if isinstance(value, int): value = str(value)
			try:
				if self._verhoeffvalidator(value): return int(value)
			except ValueError:
				raise exceptions.ValidationError(
					self.error_messages['invalid'],
					code='invalid',
					params={'value': value},
				)
		return value

	def _verhoeffvalidator(self, value):
		""" m => multiplication  , p => permutation """
		m = (	(0,1,2,3,4,5,6,7,8,9), (1,2,3,4,0,6,7,8,9,5), 
				(2,3,4,0,1,7,8,9,5,6), (3,4,0,1,2,8,9,5,6,7), 
				(4,0,1,2,3,9,5,6,7,8), (5,9,8,7,6,0,4,3,2,1),
				(6,5,9,8,7,1,0,4,3,2), (7,6,5,9,8,2,1,0,4,3), 
				(8,7,6,5,9,3,2,1,0,4), (9,8,7,6,5,4,3,2,1,0) )

		p = (	(0,1,2,3,4,5,6,7,8,9), (1,5,7,6,2,8,3,0,9,4), 
				(5,8,0,3,7,9,6,1,4,2), (8,9,1,6,0,4,3,5,2,7), 
				(9,4,5,3,1,2,6,8,7,0), (4,2,8,6,5,7,3,9,0,1),
				(2,7,9,3,8,0,6,4,1,5), (7,0,4,6,9,1,3,2,5,8) )
		i = len(value)
		j = x = 0
		while i > 0:
			i -= 1
			x = m[x][p[(j % 8)][int(value[i])]]
			j += 1
		if x == 0:
			return True
		raise ValueError

	def get_internal_type(self):
		return "IntegerField"

	def formfield(self, **kwargs):
		defaults = {'max_length': self.max_length}
		if self.null and not connection.features.interprets_empty_strings_as_nulls:
			defaults['empty_value'] = None
		defaults.update(kwargs)
		return super().formfield(**defaults)
