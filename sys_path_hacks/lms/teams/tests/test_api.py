from sys_path_hacks.warn import warn_deprecated_import

warn_deprecated_import('lms.djangoapps', 'teams.tests.test_api')

from lms.djangoapps.teams.tests.test_api import *
