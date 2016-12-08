""" rdfmarshaller adapters for dexterity content
"""

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import log
from eea.rdfmarshaller.interfaces import ISurfSession
from eea.rdfmarshaller.marshaller import GenericObject2Surf
from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapts
import rdflib
import sys


class Dexterity2Surf(GenericObject2Surf):

    adapts(IDexterityContent, ISurfSession)

    @property
    def portalType(self):
        """ Portal type """
        return self.context.portal_type.replace(' ', '')

    @property
    def prefix(self):
        """ Prefix """
        return self.portalType.lower()

    @property
    def subject(self):
        """ Subject """
        return self.context.absolute_url()

    def modify_resource(self, resource, *args, **kwds):
        plone_portal_state = self.context.restrictedTraverse(
                '@@plone_portal_state')
        portal_url = plone_portal_state.portal_url()

        workflowTool = getToolByName(self.context, "portal_workflow")
        wfs = workflowTool.getWorkflowsFor(self.context)
        wf = None
        for wf in wfs:
            if wf.isInfoSupported(self.context, "portal_workflow"):
                break

        status = workflowTool.getInfoFor(self.context, "review_state", None)
        if status is not None:
            status = ''.join([portal_url,
                              "/portal_workflow/",
                              getattr(wf, 'getId', lambda: '')(),
                              "/states/",
                              status])
            try:
                setattr(resource, '%s_%s' % ("eea", "hasWorkflowState"),
                        rdflib.URIRef(status))
            except Exception:
                log.log('RDF marshaller error for context[workflow_state]'
                        '"%s": \n%s: %s' %
                        (self.context.absolute_url(),
                         sys.exc_info()[0], sys.exc_info()[1]),
                        severity=log.logging.WARN)
        return resource
