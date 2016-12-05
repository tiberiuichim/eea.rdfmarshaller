""" Export module """
from lxml import etree
from Products.Marshall.registry import getComponent
import unicodedata


def is_pua(c):
    """ check if character is part of private unicode characters
    """
    return unicodedata.category(c) == 'Co'


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
        unicode_data = data
        if isinstance(data, str):
            unicode_data = data.decode(encoding="utf-8", errors="ignore")
        without_private_chars = [i for i in unicode_data if not is_pua(i)]
        without_private_chars = "".join(without_private_chars)
        without_private_chars = without_private_chars.encode('utf-8')
        #fix for #77766; fix non ascii characters for rdf export
        sanitized_data = etree.tostring(etree.fromstring(without_private_chars),
                                        pretty_print=True)

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
