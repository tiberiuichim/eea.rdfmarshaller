from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import log
from eea.rdfmarshaller.interfaces import ISurfResourceModifier
from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapts
from zope.interface import implements   # , providedBy
import rdflib
import sys


class WorkflowStateModifier(object):
    """Adds workflow information information to rdf resources
    """

    implements(ISurfResourceModifier)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    def run(self, resource, *args, **kwds):
        """Change the rdf resource
        """
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
