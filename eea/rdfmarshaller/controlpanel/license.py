from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from zope import schema
from zope.interface import Interface
from zope.interface import implementer
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from collective.z3cform.datagridfield.registry import DictRow


class ILicense(Interface):
    field_a = schema.ASCIILine(
        title=u"Field A",
        description=u"Something A"
    )

    field_b = schema.ASCIILine(
        title=u"Field B",
        description=u"Something B"
    )

    field_c = schema.ASCIILine(
        title=u"Field C",
        description=u"Something C"
    )


class ILicenses(Interface):
    """ Define settings data structure for licenses """

    rdfmarshaller_licenses = schema.Dict(
        title=u"Licenses",
        description=u"Define licenses.",
        key_type=schema.TextLine(title=u"License Title"),
        # value_type=schema.Text(title=u"License Text"))
        value_type=DictRow(schema=ILicense))


class LicensesEditForm(RegistryEditForm):
    """ Licenses definition edit form """
    schema = ILicenses
    label = u"Licenses definition"


class LicensesView(ControlPanelFormWrapper):
    """ Licenses edit form """

    form = LicensesEditForm

    # TODO ?
    # Customize on edit: registry record to separated fields
    # Customize on Save: separated fields to registry record


class IPortalTypeLicenses(Interface):
    """ Define settings data structure for portal types - licenses """

    rdfmarshaller_type_licenses = schema.Dict(
        title=u"Licenses",
        description=u"Choose licenses.",
        key_type=schema.Choice(
            title=u"Portal Type",
            vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"),
        value_type=schema.Choice(
            title=u"License Title",
            vocabulary="eea.rdfmarshaller.licenses")
        )


class PortalTypeLicensesEditForm(RegistryEditForm):
    """ Portal Type Licenses edit form """
    schema = IPortalTypeLicenses
    label = u"Portal type licenses settings"


class PortalTypeLicensesView(ControlPanelFormWrapper):
    """ Portal types - licenses edit form """

    form = PortalTypeLicensesEditForm


@implementer(IVocabularyFactory)
class LicensesVocabulary(object):

    def __call__(self, context):
        registry = getUtility(IRegistry)
        try:
            licenses = registry[
                "eea.rdfmarshaller.controlpanel.license.ILicenses"
                ".rdfmarshaller_licenses"]
            items = [
                SimpleTerm(str(i), str(i), str(i)) for i in licenses.keys()]
        except Exception:
            items = [SimpleTerm('WIP', 'WIP', 'WIP')]  # TODO Fix it.
        return SimpleVocabulary(items)


LicensesVocabularyFactory = LicensesVocabulary()
