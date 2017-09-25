#!/usr/bin/env python2

""" experimentation with surf.rdflib API """

import rdflib
import surf

surf.ns.register(EEA="http://www.eea.europa.eu/ontologies.rdf#")
surf.ns.register(DCAT="http://www.w3.org/ns/dcat#")
surf.ns.register(SCHEMA="http://schema.org/")
surf.ns.register(ARTICLE="http://www.eea.europa.eu/portal_types/Article#")


def make_store():
    """ store initialization
    """
    store = surf.Store(reader='rdflib', writer='rdflib',
                       rdflib_store='IOMemory')

    store.reader.graph.bind('dc', surf.ns.DC, override=True)
    store.reader.graph.bind('dcterms', surf.ns.DCTERMS, override=True)
    store.reader.graph.bind('eea', surf.ns.EEA, override=True)
    store.reader.graph.bind('geo', surf.ns.GEO, override=True)
    store.reader.graph.bind('owl', surf.ns.OWL, override=True)
    store.reader.graph.bind('dcat', surf.ns.DCAT, override=True)
    store.reader.graph.bind('schema', surf.ns.SCHEMA, override=True)
    store.reader.graph.bind('foaf', surf.ns.FOAF, override=True)
    store.reader.graph.bind('article', surf.ns.ARTICLE, override=True)

    return store


def modify(session):
    """ build the RDF
    """

    Article = session.get_class(surf.ns.EEA['Article'])
    Distribution = session.get_class(surf.ns.DCAT['Distribution'])
    Image = session.get_class(surf.ns.SCHEMA['Image'])

    indic_url = 'http://example.com/articleA'
    image_url = indic_url + '/image'
    image_download_url = indic_url + '/at_download/image'

    obj = Article(indic_url)
    obj.article_image = rdflib.URIRef(image_url)
    obj.update()

    img = Image(image_url)
    img.rdfs_label = 'depiction'
    img.schema_contentSize = '1234'

    # 'http://example.com/portal/example/image#fileInfo'
    dist = Distribution(image_url + "#fileInfo")
    dist.dcat_sizeInBytes = '1234'
    dist.dcat_downloadURL = rdflib.URIRef(image_download_url)
    dist.update()
    dist.save()

    img.eea_fileInfo = dist

    t1 = Image(indic_url + '/image_large')
    t1.schema_width = '400px'
    t1.schema_height = '200px'
    t1.update()

    t2 = Image(indic_url + '/image_preview')
    t2.schema_width = '300px'
    t2.schema_height = '100px'
    t2.update()

    img.schema_thumbnail = [t1, t2]
    img.update()

    icon = Image('http://example.com/article-icon.png')
    icon.rdfs_label = 'type_icon'
    icon.update()

    obj.foaf_depiction = [img, icon]

    obj.update()

    # obj.eea_something = ('asta', 'en')
    # obj.article_something = ('asta', 'en')
    # img.dcat_Distribution = [dist]


# Result:
# <?xml version="1.0" encoding="utf-8"?>
# <rdf:RDF
#   xmlns:foaf='http://xmlns.com/foaf/0.1/'
#   xmlns:rdfs='http://www.w3.org/2000/01/rdf-schema#'
#   xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
#   xmlns:dcat='http://www.w3.org/ns/dcat#'
#   xmlns:article='http://www.eea.europa.eu/portal_types/Article#'
#   xmlns:eea='http://www.eea.europa.eu/ontologies.rdf#'
#   xmlns:schema='http://schema.org/'
# >
#   <eea:Article rdf:about="http://example.com/articleA">
#     <foaf:depiction>
#       <schema:Image rdf:about="http://example.com/article-icon.png">
#         <rdfs:label>type_icon</rdfs:label>
#       </schema:Image>
#     </foaf:depiction>
#     <foaf:depiction>
#       <schema:Image rdf:about="http://example.com/articleA/image">
#         <schema:thumbnail
#           rdf:resource="http://example.com/articleA/image_large"/>
#         <schema:thumbnail
#           rdf:resource="http://example.com/articleA/image_preview"/>
#         <rdfs:label>depiction</rdfs:label>
#         <eea:fileInfo
#           rdf:resource="http://example.com/articleA/image#fileInfo"/>
#         <schema:contentSize>1234</schema:contentSize>
#       </schema:Image>
#     </foaf:depiction>
#     <article:image rdf:resource="http://example.com/articleA/image"/>
#   </eea:Article>
#   <schema:Image rdf:about="http://example.com/articleA/image_preview">
#     <schema:width>300px</schema:width>
#     <schema:height>100px</schema:height>
#   </schema:Image>
#   <dcat:Distribution rdf:about="http://example.com/articleA/image#fileInfo">
#     <dcat:downloadURL
#       rdf:resource="http://example.com/articleA/at_download/image"/>
#     <dcat:sizeInBytes>1234</dcat:sizeInBytes>
#   </dcat:Distribution>
#   <schema:Image rdf:about="http://example.com/articleA/image_large">
#     <schema:width>400px</schema:width>
#     <schema:height>200px</schema:height>
#   </schema:Image>
# </rdf:RDF>


def main():
    """ main function
    """
    store = make_store()
    session = surf.Session(store)

    modify(session)

    data = store.reader.graph.serialize(format='pretty-xml')
    print data

    # Test SPARQL queries
    # g = store.reader.graph
    # qu = g.query
    # res = qu("""SELECT DISTINCT ?s ?p ?v WHERE { ?s ?p ?v }""")
    # import pprint
    # pprint.pprint(list(res))


if __name__ == "__main__":
    print main()
