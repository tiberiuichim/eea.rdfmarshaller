""" Export module """
from lxml import etree
from Products.Marshall.registry import getComponent


class RDFExport(object):
    """ RDF Export """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        marshaller = getComponent('surfrdf')
        endLevel = int(self.request.get('endLevel', 1))
        _content_type, _length, data = marshaller.marshall(self.context,
                                                           endLevel=endLevel)
        #fix for #77766; fix non ascii characters for rdf export
        sanitized_data = etree.tostring(etree.fromstring(data), pretty_print=True)
        #end of fix
        self.request.response.setHeader('Content-Type',
                                        'application/rdf+xml; charset=utf-8')
        return sanitized_data

class RDFSExport(object):
    """ RDF Surf export """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        marshaller = getComponent('surfrdfs')
        _content_type, _length, data = marshaller.marshall(self.context)
        self.request.response.setHeader('Content-Type',
                                        'application/rdf+xml; charset=utf-8')
        return data
