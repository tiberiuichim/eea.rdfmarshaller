""" Archetypes specific implementation of marshalling adapters
"""

import sys

from zope.component import (adapts, getMultiAdapter, queryAdapter,
                            queryMultiAdapter)
from zope.interface import Interface, implements

import rdflib
import surf
from eea.rdfmarshaller.archetypes.interfaces import (IArchetype2Surf,
                                                     IATField2Surf,
                                                     IATVocabularyTerm)
from eea.rdfmarshaller.config import DEBUG
from eea.rdfmarshaller.interfaces import (IFieldDefinition2Surf, IObject2Surf,
                                          ISurfSession, IValue2Surf)
from eea.rdfmarshaller.marshaller import GenericObject2Surf
from OFS.interfaces import IFolder
from Products.Archetypes.interfaces import IBaseObject, IField
from Products.CMFCore.interfaces import ITypeInformation
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import log
from Products.CMFPlone.utils import _createObjectByType


class Archetype2Surf(GenericObject2Surf):
    """IArchetype2Surf implementation for AT based content items"""

    implements(IObject2Surf)
    adapts(IBaseObject, ISurfSession)

    dc_map = dict([('title', 'title'),
                   ('description', 'description'),
                   ('creation_date', 'created'),
                   ('modification_date', 'modified'),
                   ('creators', 'creator'),
                   ('subject', 'subject'),
                   ('effectiveDate', 'issued'),
                   ('expirationDate', 'expires'),
                   ('rights', 'rights'),
                   ('location', 'spatial')])

    _blacklist = ['constrainTypesMode',
                  'locallyAllowedTypes',
                  'immediatelyAddableTypes',
                  'language',
                  'allowDiscussion']
    field_map = {}

    @property
    def blacklist_map(self):
        """ These fields shouldn't be exported """
        ptool = getToolByName(self.context, 'portal_properties')
        props = getattr(ptool, 'rdfmarshaller_properties', None)

        if props:
            return list(props.getProperty('%s_blacklist'
                                          % self.portalType.lower(),
                                          props.getProperty('blacklist')))

        return self._blacklist

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
        """ Schema to Surf """
        language = self.context.Language()
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

        for field in self.context.Schema().fields():
            fieldName = field.getName()

            if fieldName in self.blacklist_map:
                continue

            # first we try with a named adapter, then a generic one
            fieldAdapter = queryMultiAdapter(
                (field, self.context, self.session),
                interface=IATField2Surf, name=fieldName)

            if not fieldAdapter:
                fieldAdapter = getMultiAdapter(
                    (field, self.context, self.session),
                    interface=IATField2Surf)

            if not fieldAdapter.exportable:
                continue

            try:
                value = fieldAdapter.value()
            except Exception:
                log.log('RDF marshaller error for context[field]'
                        '"%s[%s]": \n%s: %s' %
                        (self.context.absolute_url(), fieldName,
                         sys.exc_info()[0], sys.exc_info()[1]),
                        severity=log.logging.WARN)

            valueAdapter = queryAdapter(value, interface=IValue2Surf)

            if valueAdapter:
                value = valueAdapter(language=language)

            if not value or value == "None":
                continue

            prefix = fieldAdapter.prefix or self.prefix

            if fieldAdapter.name:
                fieldName = fieldAdapter.name
            elif fieldName in self.field_map:
                fieldName = self.field_map.get(fieldName)
            elif fieldName in self.dc_map:
                fieldName = self.dc_map.get(fieldName)
                prefix = 'dcterms'

            try:
                setattr(resource, '%s_%s' % (prefix, fieldName), value)
            except Exception:

                log.log('RDF marshaller error for context[field]'
                        '"%s[%s]": \n%s: %s' %
                        (self.context.absolute_url(), fieldName,
                         sys.exc_info()[0], sys.exc_info()[1]),
                        severity=log.logging.WARN)

        return resource


class ATFolderish2Surf(Archetype2Surf):
    """IObject2Surf implemention for Folders"""

    implements(IArchetype2Surf)
    adapts(IFolder, ISurfSession)

    def modify_resource(self, resource, currentLevel=0, endLevel=1, **kwargs):
        """ AT to Surf """
        currentLevel += 1
        resource = super(ATFolderish2Surf, self).modify_resource(
            resource, currentLevel=currentLevel, endLevel=endLevel)

        if currentLevel <= endLevel or endLevel == 0:
            resource.dcterms_hasPart = []

            catalog = getToolByName(self.context, 'portal_catalog')
            contentFilter = {
                'path': {'query': '/'.join(self.context.getPhysicalPath()),
                         'depth': 1}}
            objs = [b.getObject() for b in catalog(contentFilter,
                                                   review_state='published',
                                                   show_all=1,
                                                   show_inactive=1)]

            for obj in objs:
                resource.dcterms_hasPart.append(rdflib.URIRef(
                    obj.absolute_url()))

        return resource


class ATField2RdfSchema(GenericObject2Surf):
    """IFieldDefinition2Surf implemention for Fields;

    This is used to define rdfs schemas for objects,
    extracting their field definitions
    """

    implements(IFieldDefinition2Surf)
    adapts(IField, Interface, ISurfSession)

    _namespace = surf.ns.RDFS
    _prefix = 'rdfs'

    def __init__(self, context, fti, session):
        super(ATField2RdfSchema, self).__init__(context, session)
        self.fti = fti

    @property
    def portalType(self):
        """ portal type """

        return u'Property'

    @property
    def rdfId(self):
        """ rdf id """

        return self.context.getName().replace(' ', '')

    @property
    def subject(self):
        """ subject """

        return '%s#%s' % (self.fti.absolute_url(), self.context.getName())

    def modify_resource(self, resource, *args, **kwargs):
        """ Schema to Surf """
        context = self.context

        widget_label = (context.widget.label, u'en')
        widget_description = (context.widget.description, u'en')
        fti_title = rdflib.URIRef(u'#%s' % self.fti.Title())

        setattr(resource, 'rdfs_label', widget_label)
        setattr(resource, 'rdfs_comment', widget_description)
        setattr(resource, 'rdf_id', self.rdfId)
        setattr(resource, 'rdf_domain', fti_title)

        return resource


class FTI2Surf(GenericObject2Surf):
    """ IObject2Surf implemention for TypeInformations,

    The type informations are persistent objects found in the portal_types """

    adapts(ITypeInformation, ISurfSession)

    _namespace = surf.ns.RDFS
    _prefix = 'rdfs'

    # fields not to export, i.e Dublin Core
    blacklist_map = ['constrainTypesMode',
                     'locallyAllowedTypes',
                     'immediatelyAddableTypes',
                     'language',
                     'creation_date',
                     'modification_date',
                     'creators',
                     'subject',
                     'effectiveDate',
                     'expirationDate',
                     'contributors',
                     'allowDiscussion',
                     'rights',
                     'nextPreviousEnabled',
                     'excludeFromNav',
                     'creator'
                     ]

    def modify_resource(self, resource, *args, **kwds):
        """ Schema to Surf """

        context = self.context
        session = self.session
        # import pdb; pdb.set_trace()

        setattr(resource, 'rdfs_label', (context.Title(), u'en'))
        setattr(resource, 'rdfs_comment', (context.Description(), u'en'))
        setattr(resource, 'rdf_id', self.rdfId)
        resource.update()

        # the following hack creates a new instance of a content to
        # allow extracting the full schema, with extended fields
        # Is this the only way to do this?
        # Another way would be to do a catalog search for a portal_type,
        # grab the first object from there and use that as context

        portal_type = context.getId()
        tmpFolder = getToolByName(context, 'portal_url').getPortalObject().\
            portal_factory._getTempFolder(portal_type)
        instance = getattr(tmpFolder, 'rdfstype', None)

        if instance is None:
            try:
                instance = _createObjectByType(portal_type, tmpFolder,
                                               'rdfstype')
            except Exception:  # might be a tool class
                if DEBUG:
                    raise
                log.log('RDF marshaller error for FTI "%s": \n%s: %s' %
                        (context.absolute_url(),
                         sys.exc_info()[0], sys.exc_info()[1]),
                        severity=log.logging.WARN)

                return resource
            finally:
                catalog = getToolByName(context, 'portal_catalog')
                tmpPath = '%s/rdfstype' % '/'.join(tmpFolder.getPhysicalPath())
                brains = catalog(path=tmpPath)

                for br in brains:
                    catalog.uncatalog_object(br.getPath())

        if hasattr(instance, 'Schema'):
            schema = instance.Schema()

            for field in schema.fields():
                fieldName = field.getName()

                if fieldName in self.blacklist_map:
                    continue

                field2surf = queryMultiAdapter((field, context, session),
                                               interface=IFieldDefinition2Surf)
                field2surf.write()

        return resource


class ATVocabularyTerm2Surf(Archetype2Surf):
    """IArchetype2Surf implemention for ATVocabularyTerms"""

    implements(IArchetype2Surf)
    adapts(IATVocabularyTerm, ISurfSession)

    @property
    def blacklist_map(self):
        """ Blacklist map """

        return super(ATVocabularyTerm2Surf, self).blacklist_map + \
            ['creation_date', 'modification_date', 'creators']
