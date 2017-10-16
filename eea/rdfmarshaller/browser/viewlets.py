from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class LicenseViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/license.pt')

    @property
    def license_text(self):
        try:
            registry = getUtility(IRegistry)
            reg_types = registry[
                "eea.rdfmarshaller.controlpanel.license.IPortalTypeLicenses."
                "rdfmarshaller_type_licenses"]
            reg_licenses = registry[
                "eea.rdfmarshaller.controlpanel.license.ILicenses."
                "rdfmarshaller_licenses"]

            text = reg_licenses[reg_types[self.context.portal_type]]
        except Exception:
            text = None
        return text
