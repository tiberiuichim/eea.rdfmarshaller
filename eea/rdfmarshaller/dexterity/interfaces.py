""" rdfmarshaller interfaces """
from zope.interface import Interface, Attribute


class IDXField2Surf(Interface):
    """ Extract values from Fields, to store them in the surf session """

    def value(context):
        """ Returns the value in RDF format """

    exportable = Attribute("Is this field exportable to RDF?")
