# from xml.etree import ElementTree
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from dateutil import parser

from smpteparsers.util import (get_element, get_element_text,
        get_element_iterator, get_namespace, validate_xml)

from lxml import etree

class AssetmapError(Exception):
    pass
class AssetmapValidationError(AssetmapError):
    pass

schema_file = "screener/XSDs/am.xsd"

class Assetmap(object):
    def __init__(self, path, dcp_path, check_xml=False):
        self.path = path
        self.dcp_path = dcp_path
        self.check_xml = check_xml

        # A dictionary mapping uuids to AssetData objects containing the path,
        # volume index, offset and length of the asset
        self.assets = {}
        self.parse()

    # TODO add in XSD validation (only triggered if 'validate' is true)
    def parse(self):
        """
        Parse the ASSETMAP. Extract the id, path, volume index, offset and
        length for each asset, and the validate the paths of the downloaded
        files against the paths from the ASSETMAP file.
        """
        
        if self.check_xml:
            try:
                self.xml_validate(schema_file, self.path)
            except Exception as e:
                raise AssetmapError(e)

        tree = ET.parse(self.path)
        root = tree.getroot()
        # ElementTree prepends the namespace to all elements, so we need to extract
        # it so that we can perform sensible searching on elements.
        assetmap_ns = get_namespace(root.tag)

        self.am_id = get_element_text(root, "Id", assetmap_ns).split(":")[2]
        self.annotation_text = get_element_text(root, "AnnotationText", assetmap_ns)
        self.volume_count = get_element_text(root, "VolumeCount", assetmap_ns)
        issue_date_string = get_element_text(root, "IssueDate", assetmap_ns)
        self.issue_date = parser.parse(issue_date_string)
        self.issuer = get_element_text(root, "Issuer", assetmap_ns)
        self.creator = get_element_text(root, "Creator", assetmap_ns)

        asset_list = get_element(root, "AssetList", assetmap_ns)
        # Get the data from the ASSETMAP file
        for asset in asset_list.getchildren():
            asset_id = get_element_text(asset, "Id", assetmap_ns).split(":")[2]
            for chunklist in get_element_iterator(asset, "ChunkList", assetmap_ns):
                """
                The code below assumes that there will only ever be one chunk in a
                chunklist. Chunking is used to split files up into smaller
                parts, usually in order to provide compatability with older
                filesystems, which is not applicable for our uses.
                """
                for chunk in chunklist.getchildren():
                    a = {
                            "path": get_element_text(chunk, "Path", assetmap_ns),
                            "volume_index": get_element_text(chunk, "VolumeIndex", assetmap_ns),
                            "offset": get_element_text(chunk, "Offset", assetmap_ns),
                            "length": get_element_text(chunk, "Length", assetmap_ns)
                        }

                    asset_data = AssetData(**a)
                    self.assets[asset_id] = asset_data
                    
        self.validate()

    def xml_validate(self, schema_file, xml_file):
        """
        Call the validate_xml function in util to validate the xml file against
        the schema.
        """
        return validate_xml(schema_file, xml_file)

    def validate(self):
        """
        Check the paths of the downloaded files against the paths specified in
        the ASSETMAP file.
        """
        for asset_data in self.assets.itervalues():
            full_path = os.path.join(self.dcp_path, asset_data.path)
            if not os.path.isfile(full_path):
                raise AssetmapValidationError("File not found: {0}".format(full_path)) 


class AssetData(object):
    def __init__(self, path, volume_index, offset, length):
        self.path = path
        self.volume_index = volume_index
        self.offset = offset
        self.length = length
