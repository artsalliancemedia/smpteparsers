"""
KDM XML parser
"""
try:
    from lxml import etree as ET
except ImportError:
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

    INTEROP = 0
    SMPTE = 1

    def __init__(self, kdm_xml):
        """
        Creates a new KDM instance from a KDM XML document

        :params kdm_xml: KDM XML document in either interop of SMPTE format
        :type kdm_xml: string:
        """
        self.raw = kdm_xml
        self._parse(kdm_xml)

    @classmethod
    def from_file(cls, file_obj):
        """
        Creates a new KDM instance from a file object

        :param file_obj: file object referencing a KDM
        :type file_obj: file object
        """
        kdm = cls(file_obj.read())
        return kdm

    @property
    def kind(self):
        """
        Returns the format of the KDM XML document: interop or SMPTE
        """
        return self._kind

    def validate(self):
        """
        Validates the KDM XML document with the relevant XSDs
        TODO: this is messy and broken for interop - either find a
        better way of doing it or remove it
        """
        import os

        if self.kind == KDM.INTEROP:
            with open(os.path.join(os.path.dirname(__file__), 'xsd', 'interop.xsd'), 'r') as f:
                schema = f.read()
        elif self.kind == KDM.SMPTE:
            with open(os.path.join(os.path.dirname(__file__), 'xsd', 'smpte.xsd'), 'r') as f:
                schema = f.read()

        base_dir = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(__file__), 'xsd'))
        try:
            schema = ET.XMLSchema(ET.XML(schema))
            xmlparser = ET.XMLParser(schema=schema)
            ET.fromstring(self.raw, xmlparser)
        finally:
            os.chdir(base_dir)

    def _parse(self, kdm_xml):
        """
        Parses a KDM XML document

        :param kdm_xml: an interop or smpte KDM XML document
        :type kdm_xml: string
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
        self._kind = KDM.SMPTE
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
        self._kind = KDM.INTEROP
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

    
