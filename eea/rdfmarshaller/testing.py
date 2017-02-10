from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import eea.rdfmarshaller
        import plone.dexterity
        import plone.app.textfield

        # needed for Dexterity FTI
        self.loadZCML(package=plone.dexterity)

        # needed for DublinCore behavior
        self.loadZCML(package=plone.app.dexterity)

        # needed to support RichText in testpage
        self.loadZCML(package=plone.app.textfield)

        self.loadZCML(package=eea.rdfmarshaller)
        self.loadZCML(package=eea.rdfmarshaller, name='testing.zcml')

    def setUpPloneSite(self, portal):
        # Install the example.conference product
        self.applyProfile(portal, 'eea.rdfmarshaller:default')
        self.applyProfile(portal, 'eea.rdfmarshaller:dexterity_testfixture')


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='eea.rdfmarshaller:Integration',
    )
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='eea.rdfmarshaller:Functional',
    )
