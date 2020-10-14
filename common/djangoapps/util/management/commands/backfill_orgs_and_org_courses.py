"""
@@TODO doc
"""
from textwrap import dedent

from django.core.management.base import BaseCommand
from opaque_keys.edx.locator import LibraryLocator

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.split_mongo.split import SplitMongoModuleStore


class Command(BaseCommand):
    """
    @@TODO doc
    """
    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        _ = parser

    def handle(self, *args, **options):
        split_modulestore = _get_split_modulestore()
        org_course_pairs = _find_unique_org_course_pairs()
        org_library_pairs = _find_unique_org_library_pairs(split_modulestore)
        print(org_course_pairs)
        print(org_library_pairs)


def _get_split_modulestore():
    """
    Reach into the Mixed module store and return the Split module store.

    This will raise an exception if there is no SplitMongoModuleStore instance
    within the Mixed store.

    Returns: SplitMongoModuleStore
    """
    for store in modulestore().modulestores:
        if isinstance(store, SplitMongoModuleStore):
            return store
    raise Exception(
        "No instances of SplitMongoModuleStore in modulestore().modulestores"
    )


def _find_unique_org_course_pairs():
    """
    Returns the unique pairs of (organization short name, course run key)
    from the CourseOverviews table,
    which should contain all course runs in the system.

    Returns: set[tuple[str, str]]
    """
    # Using a set comprehension removes any duplicate (org, id) pairs.
    return {
        (
            org_short_name,
            str(course_key),
        )
        for org_short_name, course_key
        in CourseOverview.objects.all().values_list("org", "id")
        # Skip any entries with the bogus default 'org' value.
        # It would only be there for *very* outdated course overviews--there
        # should be none on edx.org, but they could plausibly exist in the community.
        if org_short_name != "outdated_entry"
    }


def _find_unique_org_library_pairs(split_modulestore):
    """
    Returns the unique pairs of (organization short name, content library key)
    from the 'library' branch of the Split module store index,
    which should contain all modulestore-based content libraries in the system.

    Note that this only considers "version 1" (aka "legacy" or "modulestore-based")
    content libraries.
    We do not consider "version 2" (aka "blockstore-based") content libraries,
    because those require a database-level link to their authoring organization,
    and thus would not need backfilling via this command.

    Arguments:
        split_modulestore (SplitMongoModuleStore)

    Returns: set[tuple[str, str]]
    """
    return {
        # library_index["course"] is actually the 'library slug',
        # which along with the 'org slug', makes up the library's key.
        # It is in the "course" field because the DB schema was designed
        # before content libraries were envisioned.
        (
            library_index["org"],
            str(LibraryLocator(library_index["org"], library_index["course"])),
        )
        for library_index
        # Again, 'course' here refers to course-like objects, which includes
        # content libraries. By specifying branch="library", we're filtering for just
        # content libraries.
        in split_modulestore.find_matching_course_indexes(branch="library")
    }
