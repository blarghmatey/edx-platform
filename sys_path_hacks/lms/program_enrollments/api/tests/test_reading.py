from sys_path_hacks.warn import warn_deprecated_import

warn_deprecated_import('lms.djangoapps', 'program_enrollments.api.tests.test_reading')

from lms.djangoapps.program_enrollments.api.tests.test_reading import *
