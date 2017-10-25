""" Test licenses feature """

from eea.rdfmarshaller.controlpanel.license import ILicenses
from eea.rdfmarshaller.controlpanel.license import IPortalTypeLicenses
from eea.rdfmarshaller.testing import INTEGRATION_TESTING
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
import unittest
from plone.app.upgrade.utils import loadMigrationProfile
# from plone.registry.record import Record
# from plone.registry import field


class TestProgramIntegration(unittest.TestCase):
    """ Integration testing """

    layer = INTEGRATION_TESTING

    def setUp(self):
        """ Setup """
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('testpage', 'test-page')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.page = self.portal['test-page']
        self.page.edit(title="Test title", description="Test description")

        loadMigrationProfile(self.portal, 'profile-eea.rdfmarshaller:default')

    def test_licenses(self):
        """ test licenses """
        licenses_settings = self.portal.unrestrictedTraverse(
            'licenses-settings')

        print "TEST @@licenses-settings exists"
        assert str(type(licenses_settings)) == \
            "<class 'Products.Five.metaclass.LicensesView'>"

        portal_type_licenses_settings = self.portal.unrestrictedTraverse(
            'portal-type-licenses-settings')

        print "TEST @@portal-type-licenses-settings exists"
        assert str(type(portal_type_licenses_settings)) == \
            "<class 'Products.Five.metaclass.PortalTypeLicensesView'>"

        print "TEST registry"
        test_licenses = [
            {
                'url': 'http://mit-license.com',
                'text': u'This is MIT license.',
                'id': 'MIT'
            },
            {
                'url': 'http://cc-license.com',
                'text': u'This is CC license.',
                'id': 'CC'
            }
        ]

        api.portal.set_registry_record(
            name='rdfmarshaller_licenses',
            value=test_licenses,
            interface=ILicenses
        )

        reg_licenses = api.portal.get_registry_record(
            'rdfmarshaller_licenses', interface=ILicenses)

        print "TEST registry: licenses are saved"
        assert reg_licenses == test_licenses

        # (Pdb) self.portal['test-page'].portal_type
        # 'testpage' - so, let's use it:
        test_portal_type_licenses = {'testpage': 'CC'}

        api.portal.set_registry_record(
            name='rdfmarshaller_type_licenses',
            value=test_portal_type_licenses,
            interface=IPortalTypeLicenses
        )

        reg_types = api.portal.get_registry_record(
            'rdfmarshaller_type_licenses', interface=IPortalTypeLicenses)

        print "TEST registry: licenses-types are saved"
        assert reg_types == test_portal_type_licenses

        print "TEST license viewlet rendering"
        page = self.portal['test-page']()
        assert """<script type="application/ld+json">""" in page
        assert """http://cc-license.com""" in page
        assert """http://mit-license.com""" not in page
        assert """odrs:copyrightNotice""" in page


def test_suite():
    """ test suite """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
