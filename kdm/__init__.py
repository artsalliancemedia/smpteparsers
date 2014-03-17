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
        ap_el = get_element(root, 'AuthenticatedPublic', kdm_ns)
        self.id = strip_urn(get_element_text(ap_el, 'MessageId', kdm_ns))
        self.annotation_text = get_element_text(ap_el, 'AnnotationText', kdm_ns)
        self.issue_date = get_element_text(ap_el, 'IssueDate', kdm_ns)
        re_el = get_element(ap_el, 'RequiredExtensions', kdm_ns)
        self.cpl_id = strip_urn(get_element_text(re_el, 'CompositionPlaylistId', kdm_ns))
        self.content_title_text = get_element_text(re_el, 'ContentTitleText', kdm_ns)
        self.start_date = get_element_text(re_el, 'ContentKeysNotValidBefore', kdm_ns)
        self.end_date = get_element_text(re_el, 'ContentKeysNotValidAfter', kdm_ns)