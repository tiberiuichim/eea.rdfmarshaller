from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import json


REGISTRY_TYPE_LICENSES = "eea.rdfmarshaller.controlpanel.license." + \
    "IPortalTypeLicenses.rdfmarshaller_type_licenses"

REGISTRY_LICENSES = "eea.rdfmarshaller.controlpanel.license." + \
    "ILicenses.rdfmarshaller_licenses"


class LicenseViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/license.pt')

    @property
    def license_text(self):
        """ Return assigned license for portal_type of this context or None

            Example:
            https://github.com/theodi/open-data-licensing/blob/master/
                    examples/simple-json-ld.json
        """

        registry = getUtility(IRegistry)
        reg_types = registry.get(REGISTRY_TYPE_LICENSES, None)
        reg_licenses = registry.get(REGISTRY_LICENSES, None)

        license_url = "www.google.com"
        license_title = "License Title Here"
        # TODO Update this & template
        # if reg_licenses is not None and reg_types is not None:
        #     license_id = reg_types.get(self.context.portal_type, None)
        #     if license_id is not None:
        #         text = reg_licenses.get(license_id, None)

        text = json.dumps(
            {
                "@context": {
                    "dcat": "http://www.w3.org/ns/dcat#",
                    "dct": "http://purl.org/dc/terms/",
                    "odrs": "http://schema.theodi.org/odrs#",
                    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                },

                "@id": self.context.absolute_url(),
                "@type": "dcat:Dataset",
                "dct:title": self.context.title,

                "dct:license": {
                    "@id": license_url,
                    "dct:title": license_title
                },

                "dct:rights": {
                    "rdfs:label": "Rights Statement",
                    "@id": "http://gov.example.org/dataset/example#rights",
                    "odrs:copyrightNotice": "Crown copyright 2013",
                    "odrs:attributionText": "Example Department",

                    "odrs:attributionURL": {
                        "@id": "http://gov.example.org/dataset/example"
                    },
                    "odrs:contentLicense": {
                        "@id": license_url
                    },
                    "odrs:dataLicense": {
                        "@id": license_url
                    }
                }
            }
        )

        return text
