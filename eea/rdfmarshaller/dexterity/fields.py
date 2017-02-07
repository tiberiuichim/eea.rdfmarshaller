from Acquisition import aq_base
from Products.CMFPlone import log
from eea.rdfmarshaller.archetypes.fields import Value2Surf
from eea.rdfmarshaller.dexterity.interfaces import IDXField2Surf
from eea.rdfmarshaller.interfaces import ISurfSession
from plone.app.textfield.value import RichTextValue
from zope.component import adapts
from zope.interface import implements, Interface
import sys


class DXField2Surf(object):
    """Base implementation of IDXField2Surf """

    implements(IDXField2Surf)
    # adapts(IField, Interface, ISurfSession)
    adapts(Interface, Interface, ISurfSession)

    exportable = True
    prefix = None   # override the prefix for this predicate
    name = None     # this will be the predicate name (fieldname)

    def __init__(self, field, context, session):
        self.field = field
        self.context = context
        self.session = session

        self.name = self.field.__name__

    def value(self):
        """ Value """
        value = getattr(aq_base(self.context), self.name, None)
        try:
            if callable(value):
                value = value()
            print "Returning '{}' for field {}".format(value, self.name)
            return value
        except Exception:
            log.log('RDF marshaller error for context[field]'
                    '"%s[%s]": \n%s: %s' %
                    (self.context.absolute_url(), self.name,
                     sys.exc_info()[0], sys.exc_info()[1]),
                    severity=log.logging.WARN)

            return None


class RichValue2Surf(Value2Surf):
    adapts(RichTextValue)

    def __init__(self, value):
        self.value = value.output
