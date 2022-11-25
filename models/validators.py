from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.utils.regex_helper import _lazy_re_compile




@deconstructible
class CheckSumValidator:
	""" BaseValidate for checksum """

	message = _('Ensure this value is not a checksum value.')
	code = 'invalid'

	def __init__(self, message=None, code=None):
		if message is not None: self.message = message
		if code is not None: self.code = code

	def __call__(self, value):
		cleaned = self.clean(value)
		if not self.checksum(cleaned):
			raise ValidationError(
				self.message, 
				code=self.code, 
				params={'value': cleaned}
			)

	def checksum(self, value):
		return True

	def clean(self, x):
		if isinstance(x, int):
			return str(x)
		return x



@deconstructible
class VerhoeffValidator(CheckSumValidator):
	"""Calculate and verify check digits using Verhoeff's algorithm"""
	""" Reference https://codereview.stackexchange.com/questions/221229/verhoeff-check-digit-algorithm """

	MULTIPLICATION_TABLE = (
		(0, 1, 2, 3, 4, 5, 6, 7, 8, 9), (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
		(2, 3, 4, 0, 1, 7, 8, 9, 5, 6), (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
		(4, 0, 1, 2, 3, 9, 5, 6, 7, 8), (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
		(6, 5, 9, 8, 7, 1, 0, 4, 3, 2), (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
		(8, 7, 6, 5, 9, 3, 2, 1, 0, 4), (9, 8, 7, 6, 5, 4, 3, 2, 1, 0) )

	INVERSE_TABLE = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)

	PERMUTATION_TABLE = (
		(0, 1, 2, 3, 4, 5, 6, 7, 8, 9), (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
		(5, 8, 0, 3, 7, 9, 6, 1, 4, 2), (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
		(9, 4, 5, 3, 1, 2, 6, 8, 7, 0), (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
		(2, 7, 9, 3, 8, 0, 6, 4, 1, 5), (7, 0, 4, 6, 9, 1, 3, 2, 5, 8) )

	# def _calculate(self, input_: str) -> str:
	#     """Calculate the check digit using Verhoeff's algorithm"""
	#     check_digit = 0
	#     for i, digit in enumerate(reversed(input_), 1):
	#         col_idx = self.PERMUTATION_TABLE[i % 8][int(digit)]
	#         check_digit = self.MULTIPLICATION_TABLE[check_digit][col_idx]
	#     return str(self.INVERSE_TABLE[check_digit])

	def checksum(self, value: str) -> bool:
		"""Validate the check digit using Verhoeff's algorithm"""
		check_digit = 0
		for i, digit in enumerate(reversed(value)):
			col_index = self.PERMUTATION_TABLE[i % 8][int(digit)]
			check_digit = self.MULTIPLICATION_TABLE[check_digit][col_index]
		return self.INVERSE_TABLE[check_digit] == 0



@deconstructible
class GSTINValidator(CheckSumValidator):
	""" 
		Checks a values validates as a GST Number.
		NOTE:
			A GST number is 15 digit alphanumeric.
			eg. 24 AAACB5343E 1 Z 7
			- First 2 digits are state code ranges 01-37
			- Next 10 digits is PAN Card number
				* First 3 are alphabets ranges from AAA-ZZZ
				* Next alphabet is either C,P,H,F,A,T,B,L,J,G,E
				* Next alphabet of Surname or Name
				* Next 4 digits range from 0001 to 9999
				* Next alphabetic check digit
			- 13th alphabets assigned based on the no. of reg. within a state
			- 14th alphabets will be Z by default
			- Last digit will be for check code. It may be an alphabet or a number.
	"""

	message = _('Enter a valid GST number.')

	def checksum(self, value: str) -> bool:
		checker = value[-1]
		gst_no = value[:-1]
		test = [int(digit) if digit.isdigit() else (ord(digit) - 55) for digit in gst_no]
		test = [(value * (index % 2 + 1)) for (index, value) in list(enumerate(test))]
		test = [(int(value/36) + value%36) for value in test]
		check_sum = (36 - sum(test) % 36)
		check_sum = str(check_sum) if (check_sum < 10) else chr(check_sum + 55)
		return True if (checker == check_sum) else False


@deconstructible
class PANValidator(CheckSumValidator):
	message = _('Enter a valid PAN number.')
	""" Checks a values validates as a PAN Number.
		NOTE:
			A PAN number is 10 digit alphanumeric.
			eg. AAA C B 5343 E
			- First 3 are alphabets ranges from AAA-ZZZ
			- Next alphabet is either C,P,H,F,A,T,B,L,J,G,E
			- Next alphabet of Surname or Name
			- Next 4 digits range from 0001 to 9999
			- Next alphabetic check digit
	"""
	PAN_REGEX = r'^[A-Z]{3}[ABCEFGHJLPT]{1}[A-Z]{1}\d{4}[A-Z]{1}$'
	# GSTIN_REGEX = r'^(3[0-7]|[1-2][0-9]|0[1-9])%s\d[Z]{1}[A-Z\d]{1}$' % PAN_REGEX

	def __init__(self, message=None, code=None):
		super().__init__(message, code)
		self._regex = _lazy_re_compile(self.PAN_REGEX)

	def checksum(self, value):
		regex_matches = self._regex.search(self.clean(value))
		if regex_matches:
			return True
		return False



@deconstructible
class NonZeroValidator:
	"""Validate that the string doesn't contain the null character."""
	message = _('Zero is not valid.')
	code = 'not_zero'

	def __init__(self, message=None):
		if message:
			self.message = message

	def __call__(self, value):
		cleaned = self.clean(value)
		params = {'show_value': cleaned, 'value': value}
		if cleaned in [0, '0']:
			raise ValidationError(self.message, code=self.code, params=params)

	def clean(self, x):
		print(type(x))
		return x
