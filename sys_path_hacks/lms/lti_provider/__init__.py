from sys_path_hacks.warn import warn_deprecated_import

warn_deprecated_import('lms.djangoapps', 'lti_provider')

from lms.djangoapps.lti_provider import *
