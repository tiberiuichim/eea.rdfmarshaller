""" Archetypes fields
"""

from Products.Archetypes.interfaces import IField, IFileField
from Products.CMFPlone import log
from eea.rdfmarshaller.archetypes.interfaces import IATField2Surf
from eea.rdfmarshaller.archetypes.interfaces import IReferenceField
from eea.rdfmarshaller.interfaces import ISurfSession
from zope.component import adapts
from zope.interface import implements, Interface
import rdflib
import surf
import sys


class ATField2Surf(object):
    """Base implementation of IATField2Surf """

    implements(IATField2Surf)
    adapts(IField, Interface, ISurfSession)

    exportable = True
    prefix = None   # override the prefix for this predicate
    name = None     # this will be the predicate name (fieldname)

    def __init__(self, field, context, session):
        self.field = field
        self.context = context
        self.session = session

    def value(self):
        """ Value """
        try:
            return self.field.getAccessor(self.context)()
        except Exception:
            log.log('RDF marshaller error for context[field]'
                    '"%s[%s]": \n%s: %s' %
                    (self.context.absolute_url(), self.field.getName(),
                     sys.exc_info()[0], sys.exc_info()[1]),
                    severity=log.logging.WARN)

            return None


class ATFileField2Surf(ATField2Surf):
    """IATField2Surf implementation for File fields"""

    implements(IATField2Surf)
    adapts(IFileField, Interface, ISurfSession)

    exportable = True
    prefix = "eea"
    name = "fileInfo"

    def value(self):
        """ The desired output is similar to:
        <datafile:DataFile ...
        ...
        <eea:fileInfo>
         <dcat:Distribution rdf:about="#dist">
          <dcat:sizeInBytes rdf:datatype="XMLSchema#long">X</dcat:sizeInBytes>
          <dcat:downloadURL rdf:resource="[url]/at_download/file"/>
        ...
        </datafile:DataFile>
        """
        # only the size and download ULR are returned
        Distribution = self.session.get_class(surf.ns.DCAT.Distribution)
        fileDistribution = self.session.get_resource('#distribution',
                                                     Distribution)

        value = self.field.getAccessor(self.context)()
        # 22047 check if value isn't a false value, images with no data
        # will return an empty string
        size = value.get_size() if value else 0
        fileDistribution[surf.ns.DCAT['sizeInBytes']] = size

        url = ''.join([self.context.absolute_url(),
                       "/at_download/",
                       self.field.getName()])
        fileDistribution[surf.ns.DCAT['downloadURL']] = rdflib.URIRef(url)
        fileDistribution.update()

        return [fileDistribution]


class ATReferenceField2Surf(ATField2Surf):
    """IATField2Surf implementation for Reference fields"""

    implements(IATField2Surf)
    adapts(IReferenceField, Interface, ISurfSession)

    def value(self):
        """ Value """
        value = self.field.getAccessor(self.context)()

        # some reference fields are single value only
        if not isinstance(value, (list, tuple)):
            value = [value]

        value = [v for v in value if v]     # the field might have been empty

        return [rdflib.URIRef(obj.absolute_url()) for obj in value]
