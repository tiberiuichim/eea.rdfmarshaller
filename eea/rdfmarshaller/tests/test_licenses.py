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
        reg_types = api.portal.get_registry_record(
            'rdfmarshaller_type_licenses', interface=IPortalTypeLicenses)
        reg_licenses = api.portal.get_registry_record(
            'rdfmarshaller_licenses', interface=ILicenses)

        assert reg_types is None
        assert reg_licenses is None

        # save_button = licenses_settings.form.buttons.items()[0][1]
        # save_handler = licenses_settings.form.handlers.getHandler(
        # save_button)
        # save_handler.func(licenses_settings.form_instance, save_button)

        # import pdb; pdb.set_trace()


def test_suite():
    """ test suite """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
