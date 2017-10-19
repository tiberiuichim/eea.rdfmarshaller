from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


REGISTRY_TYPE_LICENSES = "eea.rdfmarshaller.controlpanel.license." + \
    "IPortalTypeLicenses.rdfmarshaller_type_licenses"

REGISTRY_LICENSES = "eea.rdfmarshaller.controlpanel.license." + \
    "ILicenses.rdfmarshaller_licenses"


class LicenseViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/license.pt')

    @property
    def license_text(self):
        """ Return assigned license for portal_type of this context or None
        """
        registry = getUtility(IRegistry)
        reg_types = registry.get(REGISTRY_TYPE_LICENSES, None)
        reg_licenses = registry.get(REGISTRY_LICENSES, None)
        text = None
        # TODO Update this & template
        # if reg_licenses is not None and reg_types is not None:
        #     license_id = reg_types.get(self.context.portal_type, None)
        #     if license_id is not None:
        #         text = reg_licenses.get(license_id, None)
        return text
