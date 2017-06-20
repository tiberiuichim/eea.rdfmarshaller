""" Base module """

import logging
import sys
from Products.ATVocabularyManager.config import TOOL_NAME as VOCABTOOL
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.log import logger
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Zope2.App.zcml import load_config
import eea.rdfmarshaller
import eea.depiction

PloneTestCase.installProduct('ATVocabularyManager')
PloneTestCase.installProduct('eea.depiction')

PRODUCTS = ['ATVocabularyManager', 'eea.depiction']
PROFILES = ['eea.rdfmarshaller:default']


@onsetup
def setup_rdfmarshaller():
    """ Setup """

    fiveconfigure.debug_mode = True
    load_config('configure.zcml', eea.rdfmarshaller)
    load_config('testing.zcml', eea.rdfmarshaller)

    fiveconfigure.debug_mode = False


@onsetup
def setup_depiction():
    """ Setup """

    load_config('configure.zcml', eea.depiction)
    PloneTestCase.installPackage('eea.depiction')


setup_rdfmarshaller()
setup_depiction()
PloneTestCase.setupPloneSite(
        products=PRODUCTS,
        extension_profiles=['eea.rdfmarshaller:testfixture'])


class FunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ Functional Test Case """

    def afterSetUp(self):
        """ After setup """
        self.setRoles(['Manager'])

    def enableDebugLog(self):
        """ Enable context.plone_log() output from Python scripts """
        logger.root.setLevel(logging.WARN)
        logger.root.addHandler(logging.StreamHandler(sys.stdout))

    def setupVocabularies(self):
        """ Setup vocabularies """
        portal = self.portal
        atvm = getToolByName(portal, VOCABTOOL, None)
        if atvm is None:
            return
        vocabs = {
            'eea.rdfmarshaller.vocab.testing': (
              (u'air pollution', "Air pollution"),
              (u'climate change', "Climate change mitigation"),
              (u'biodiversity', "Nature protection and biodiversity"),
              (u'land', "Land use"),
              (u'freshwater', "Freshwater"),
              (u'waste', "Waste"),
             ),
            }

        # wftool = portal.portal_workflow
        for vkey in vocabs:
            atvm.invokeFactory('SimpleVocabulary', vkey)
            simple = atvm.getVocabularyByName(vkey)
            for (key, val) in vocabs[vkey]:
                simple.addTerm(key, val)
                # term = simple[key]
                # wftool.doActionFor(term, 'publish')
