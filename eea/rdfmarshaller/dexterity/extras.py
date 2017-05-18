from collective.cover.interfaces import ICover
import sys
from Products.CMFPlone import log
from eea.rdfmarshaller.interfaces import ISurfResourceModifier
from zope.component import adapts
from zope.interface import implements


class CoverTilesModifier(object):
    """Adds tiles information to rdf resources
    """

    implements(ISurfResourceModifier)
    adapts(ICover)

    def __init__(self, context):
        self.context = context

    def run(self, resource, *args, **kwds):
        """Change the rdf resource
        """
        uids = self.context.list_tiles()
        value = ''
        for uid in uids:
            tile = self.context.get_tile(uid)
            text = tile.data.get('text', None)
            if text:
                value += text.output
        if value:
            try:
                setattr(resource, '%s_%s' % ("eea", "cover_tiles"),
                        [value])
            except Exception:
                log.log('RDF marshaller error for context[tiles]'
                        '"%s[": \n%s: %s' %
                        (self.context.absolute_url(),
                         sys.exc_info()[0], sys.exc_info()[1]),
                        severity=log.logging.WARN)
        return resource
