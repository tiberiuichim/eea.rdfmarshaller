from zope.interface import Interface


class IFallbackDCDescription(Interface):
    """ Interface for a fallback implementation of DublinCore Description

    It should be used if the normal DC Description is empty
    """

    def Description():
        """ Return plain text description """
