import re
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


AlphabeticStartValidator = RegexValidator(
    re.compile(r'^[a-z]'),
    _('This field must start with alphabetic characters.')
)

AlphaNumEndValidator = RegexValidator(
    re.compile(r'[a-z0-9]$', re.I),
    _('This field must end with alphanumeric characters.')
)

AlphaNumDashValidator = RegexValidator(
    re.compile(r'^[a-z0-9]([a-z0-9]|-[^-])+[a-z0-9]$', re.I),
    _('This field can only contain alphanumeric characters with single dashes in between.')
)

ThreeCharacterMinValidator = RegexValidator(
    re.compile(r'.{3,}'),
    _('This field must be 3 characters or more.')
)

SixCharacterMinValidator = RegexValidator(
    re.compile(r'.{6,}'),
    _('This field must be 6 characters or more.')
)
