try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from smpteparsers.util import get_element_text
from smpteparsers.util import get_element_iterator
from smpteparsers.util import get_namespace
from smpteparsers.util import strip_urn

class KDMBundleCatalog(object):
    """
    KDM bundle catalog XML document
    """

    @classmethod
    def from_string(cls, catalog_str):
        """
        Creates a new KDM instance from a string

        :param kdm_str: KDM XML document
        "type kdm_str: string
        """
        catalog = cls()
        catalog._parse(catalog_str)
        return catalog

    def _parse(self, catalog_str):
        """
        Parses a KDM bundle catalog XML string
        """
        root = ET.fromstring(catalog_str)
        cat_ns = get_namespace(root.tag)
        self.id = strip_urn(get_element_text(root, 'Id', cat_ns))
        self.annotation_text = get_element_text(root, 'AnnotationText', cat_ns)
        self.creator = get_element_text(root, 'Creator', cat_ns)
        self.cpl_ids = []
        self.kdm_paths = []
        self.start_dates = []
        self.end_dates = []
        for kdm_list_el in get_element_iterator(root, 'KDMFileList', cat_ns):
            for kdm_el in kdm_list_el.getchildren():
                self.cpl_ids.append(strip_urn(get_element_text(kdm_el, 'CPLId', cat_ns)))
                self.kdm_paths.append(get_element_text(kdm_el, 'FilePath', cat_ns))
                self.start_dates.append(get_element_text(kdm_el, 'ContentKeysNotValidBefore', cat_ns))
                self.end_dates.append(get_element_text(kdm_el, 'ContentKeysNotValidAfter', cat_ns))