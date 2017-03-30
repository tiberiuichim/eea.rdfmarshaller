#!/usr/bin/env python2

import logging
import rdflib
import surf


surf.ns.register(EEA="http://www.eea.europa.eu/ontologies.rdf#")
surf.ns.register(DCAT="http://www.w3.org/ns/dcat#")
surf.ns.register(SCHEMA="http://schema.org/")


def make_store():

    store = surf.Store(reader='rdflib', writer='rdflib',
                       rdflib_store='IOMemory')
    store.log.setLevel(logging.CRITICAL)
    store.writer.log.setLevel(logging.CRITICAL)

    store.reader.graph.bind('dc', surf.ns.DC, override=True)
    store.reader.graph.bind('dcterms', surf.ns.DCTERMS, override=True)
    store.reader.graph.bind('eea', surf.ns.EEA, override=True)
    store.reader.graph.bind('geo', surf.ns.GEO, override=True)
    store.reader.graph.bind('owl', surf.ns.OWL, override=True)
    store.reader.graph.bind('dcat', surf.ns.DCAT, override=True)
    store.reader.graph.bind('schema', surf.ns.SCHEMA, override=True)
    store.reader.graph.bind('foaf', surf.ns.FOAF, override=True)

    return store


def modify(session):

    Indicator = session.get_class(surf.ns.EEA['Indicator'])
    obj = Indicator('http://example.com/indicatorA')

    Image = session.get_class(surf.ns.SCHEMA['Image'])

    img = Image('http://example.com/portal/example')
    img.rdfs_label = 'depiction'
    img.schema_logo = 'http://example.com/indicator.jpg'

    t1 = Image('http://example.com/something/image_large')
    t1.schema_width = '400px'
    t1.schema_height = '200px'
    t1.update()

    t2 = Image('http://example.com/something-else/image_large')
    t2.schema_width = '400px'
    t2.schema_height = '200px'
    t2.update()

    img.schema_thumbnail = [t1, t2]
    img.update()

    icon = Image('http://example.com/indicator-icon.png')
    icon.rdfs_label = 'type_icon'
    icon.update()

    obj.foaf_depiction = [img, icon]

    obj.update()


# Result:
"""
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
  xmlns:foaf='http://xmlns.com/foaf/0.1/'
  xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
  xmlns:eea='http://www.eea.europa.eu/ontologies.rdf#'
  xmlns:rdfs='http://www.w3.org/2000/01/rdf-schema#'
  xmlns:schema='http://schema.org/'
>
  <eea:Indicator rdf:about="http://example.com/indicatorA">
    <foaf:depiction>
      <schema:Image rdf:about="http://example.com/indicator-icon.png">
        <rdfs:label>type_icon</rdfs:label>
      </schema:Image>
    </foaf:depiction>
    <foaf:depiction>
      <schema:Image rdf:about="http://example.com/portal/example">
        <schema:logo>http://example.com/indicator.jpg</schema:logo>
        <rdfs:label>depiction</rdfs:label>
        <schema:thumbnail rdf:resource="http://example.com/something/image_large"/>
        <schema:thumbnail rdf:resource="http://example.com/something-else/image_large"/>
      </schema:Image>
    </foaf:depiction>
  </eea:Indicator>
  <schema:Image rdf:about="http://example.com/something/image_large">
    <schema:width>400px</schema:width>
    <schema:height>200px</schema:height>
  </schema:Image>
  <schema:Image rdf:about="http://example.com/something-else/image_large">
    <schema:width>400px</schema:width>
    <schema:height>200px</schema:height>
  </schema:Image>
</rdf:RDF>

"""


def main():
    store = make_store()
    session = surf.Session(store)

    modify(session)

    data = store.reader.graph.serialize(format='pretty-xml')
    return data


if __name__ == "__main__":
    print main()
