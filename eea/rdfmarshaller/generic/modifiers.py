from eea.rdfmarshaller.generic.interfaces import IFallbackDCDescription
from eea.rdfmarshaller.interfaces import ISurfResourceModifier
from Products.CMFCore.interfaces import IContentish, IDublinCore
from zope.component import adapts, queryAdapter
from zope.interface import Interface, implements


class DCDescriptionModifier(object):
    """Adds dcterms:references
    """

    implements(ISurfResourceModifier)
    adapts(IContentish)

    def __init__(self, context):
        self.context = context

    def run(self, resource, *args, **kwds):
        """Change the rdf resource
        """

        desc = ""
        base = queryAdapter(IDublinCore, self.context)

        if base is not None:
            desc = base.Description()

        if not (desc and desc.strip()):
            fallback = queryAdapter(self.context, IFallbackDCDescription)

            if fallback is not None:
                desc = fallback.Description()

        if desc:
            resource.dcterms_description = desc


class GenericFallbackDCDescription(object):
    """ Generic Fallback DC Description implementation

    This returns None for the Description. It is meant to be overridden

    for custom behavior.
    """

    implements(IFallbackDCDescription)
    adapts(Interface)

    def __init__(self, context):
        self.context = context

    def Description(self):
        return None
