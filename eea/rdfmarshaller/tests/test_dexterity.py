""" Test dexterity """

import unittest
from eea.rdfmarshaller.testing import INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from zope.component import getMultiAdapter
import lxml.etree


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

    def test_rdf_view(self):
        """ test rdf view """
        req = self.portal.REQUEST
        rdf = getMultiAdapter((self.page, req), name="rdf")()

        assert "<dcterms:creator>test_user_1_</dcterms:creator>" in rdf
        assert "<dcterms:description>Test description</dcterms:description>" \
            in rdf
        assert "<dcterms:title>Test title</dcterms:title>" in rdf

    def test_rdfs_view(self):
        """ test rdfs view """
        ptypes = self.portal['portal_types']
        testpage_fti = ptypes['testpage']
        req = self.portal.REQUEST
        view = getMultiAdapter((testpage_fti, req), name="rdf")
        rdf = view()
        if isinstance(rdf, unicode):
            rdf = rdf.encode()
        e = lxml.etree.fromstring(rdf)
        ns = {
            'RDF': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            'RDFS': "http://www.w3.org/2000/01/rdf-schema#"
        }
        props = e.xpath('//RDFS:Property', namespaces=ns)
        fields = [x.xpath('RDF:id', namespaces=ns)[0].text for x in props]
        assert set([f for f in fields if f in ['description', 'effective',
                                               'expires', 'subjects', 'title']
                    ])


def test_suite():
    """ test suite """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
