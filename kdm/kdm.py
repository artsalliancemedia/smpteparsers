"""
KDM XML parser
"""

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from smpteparsers.util import get_element_text
from smpteparsers.util import get_element
from smpteparsers.util import get_namespace
from smpteparsers.util import strip_urn

class KDM(object):
    """
    Parses data from KDM XML data
    """

    @classmethod
    def from_string(cls, kdm_str):
        """
        Creates a new KDM instance from a string

        :param kdm_str: KDM XML document
        "type kdm_str: string
        """
        kdm = cls()
        kdm._parse(kdm_str)
        return kdm

    def _parse(self, kdm_xml):
        """
        Parses a KDM XML document
        """
        root = ET.fromstring(kdm_xml)
        kdm_ns = get_namespace(root.tag)
        if kdm_ns.startswith('http://www.smpte-ra.org'):
            self._parse_smpte(root)
        else:
            self._parse_interop(root)

    def _parse_smpte(self, root):
        """
        Parses a SMPTE KDM

        :params root: the root element of the XML document
        :type root: ElementTree Element
        """
        smpte_etm_ns = get_namespace(root.tag)
        ap_el = get_element(root, 'AuthenticatedPublic', smpte_etm_ns)
        self.id = strip_urn(get_element_text(ap_el, 'MessageId', smpte_etm_ns))
        self.annotation_text = get_element_text(ap_el, 'AnnotationText', smpte_etm_ns)
        self.issue_date = get_element_text(ap_el, 'IssueDate', smpte_etm_ns)
        re_el = get_element(ap_el, 'RequiredExtensions', smpte_etm_ns)
        smpte_kdm_ns ='http://www.smpte-ra.org/schemas/430-1/2006/KDM'
        kdm_re_el = get_element(re_el, 'KDMRequiredExtensions', smpte_kdm_ns)
        self.cpl_id = strip_urn(get_element_text(kdm_re_el, 'CompositionPlaylistId', smpte_kdm_ns))
        self.content_title_text = get_element_text(kdm_re_el, 'ContentTitleText', smpte_kdm_ns)
        self.start_date = get_element_text(kdm_re_el, 'ContentKeysNotValidBefore', smpte_kdm_ns)
        self.end_date = get_element_text(kdm_re_el, 'ContentKeysNotValidAfter', smpte_kdm_ns)


    def _parse_interop(self, root):
        """
        Parses a KDM in interop format

        :params root: the root element of the XML document
        :type root: ElementTree Element
        """
        interop_kdm_ns = get_namespace(root.tag)
        ap_el = get_element(root, 'AuthenticatedPublic', interop_kdm_ns)
        self.id = strip_urn(get_element_text(ap_el, 'MessageId', interop_kdm_ns))
        self.annotation_text = get_element_text(ap_el, 'AnnotationText', interop_kdm_ns)
        self.issue_date = get_element_text(ap_el, 'IssueDate', interop_kdm_ns)
        re_el = get_element(ap_el, 'RequiredExtensions', interop_kdm_ns)
        self.cpl_id = strip_urn(get_element_text(re_el, 'CompositionPlaylistId', interop_kdm_ns))
        self.content_title_text = get_element_text(re_el, 'ContentTitleText', interop_kdm_ns)
        self.start_date = get_element_text(re_el, 'ContentKeysNotValidBefore', interop_kdm_ns)
        self.end_date = get_element_text(re_el, 'ContentKeysNotValidAfter', interop_kdm_ns)