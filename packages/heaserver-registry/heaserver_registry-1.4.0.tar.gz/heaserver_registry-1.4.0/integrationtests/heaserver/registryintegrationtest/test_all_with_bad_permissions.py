from .componentpermissionstestcase import ComponentPermissionsTestCase
from heaserver.service.testcase.mixin import PermissionsGetOneMixin


class TestGetOneComponentWithBadPermissions(ComponentPermissionsTestCase, PermissionsGetOneMixin):
    """A test case class for testing GET one requests with bad permissions."""
    async def test_get_content_bad_permissions(self) -> None:
        self.skipTest('GET content not defined')

    async def test_get_content_bad_permissions_status(self) -> None:
        self.skipTest('GET content not defined')
