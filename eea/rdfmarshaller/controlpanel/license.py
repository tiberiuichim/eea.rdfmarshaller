from Products.Five.browser import BrowserView
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
# from plone.directives import form
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface


class ILicenses(Interface):
    """ Define settings data structure """

    licenses = schema.Dict(
        title=u"Licenses",
        description=u"Choose licenses.")


class LicensesEditForm(RegistryEditForm):
    """
    Define form logic
    """
    schema = ILicenses
    label = u"Silvuple settings"


# class LicensesView(BrowserView):
#     """
#     """
#
#     def render(self):
#         view_factor = layout.wrap_form(
#                 LicensesEditForm, ControlPanelFormWrapper)
#         view = view_factor(self.context, self.request)
#         return view()

class LicensesView(ControlPanelFormWrapper):
    """Control panel form wrapper."""

    form = LicensesEditForm
