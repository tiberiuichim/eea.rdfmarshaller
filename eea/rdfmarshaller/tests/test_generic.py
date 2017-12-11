""" Test generic functionality """

import unittest

from lxml.etree import fromstring

from eea.rdfmarshaller.testing import INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, setRoles
from zope.component import getMultiAdapter


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

    def test_missing_description(self):
        rdf = getMultiAdapter((self.page, self.page.REQUEST), name='rdf')
        out = rdf()
        e = fromstring(out.encode('utf-8'))
        desc = e.xpath('//dcterms:description',
                       namespaces={"dcterms": "http://purl.org/dc/terms/"})

        assert not desc

    def test_default_description(self):
        self.page.edit(title="Test title", description="Test description")
        rdf = getMultiAdapter((self.page, self.page.REQUEST), name='rdf')
        out = rdf()
        e = fromstring(out.encode('utf-8'))
        desc = e.xpath('//dcterms:description',
                       namespaces={"dcterms": "http://purl.org/dc/terms/"})

        assert len(desc) == 1
        assert desc[0].text == 'Test description'

    def test_fallback_description(self):

        from eea.rdfmarshaller.generic.interfaces import IFallbackDCDescription
        from zope.component import getGlobalSiteManager
        from zope.interface import Interface

        class Custom(object):
            def __init__(self, context):
                self.context = context

            def Description(self):
                return "custom description"

        gsm = getGlobalSiteManager()
        gsm.registerAdapter(Custom, [Interface], IFallbackDCDescription)

        rdf = getMultiAdapter((self.page, self.page.REQUEST), name='rdf')
        out = rdf()
        e = fromstring(out.encode('utf-8'))
        desc = e.xpath('//dcterms:description',
                       namespaces={"dcterms": "http://purl.org/dc/terms/"})

        assert len(desc) == 1
        assert desc[0].text == 'custom description'

        gsm.adapters.unregister([Interface], IFallbackDCDescription, '')


def test_suite():
    """ test suite """

    return unittest.defaultTestLoader.loadTestsFromName(__name__)
