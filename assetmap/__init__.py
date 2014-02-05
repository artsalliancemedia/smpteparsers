import os
from lxml import etree
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from smpteparsers.util.date_utils import parse_date
from smpteparsers.util import get_element, get_element_text, get_element_iterator, get_namespace, validate_xml, create_child_element

class AssetmapError(Exception):
    pass
class AssetmapValidationError(AssetmapError):
    pass

class Assetmap(object):
    def __init__(self, path, parse=True):
        self.path = path

        # A list of the assets contained in the DCP.
        self.assets = {}

        if parse:
            self.parse()

    def __unicode__(self):
        root = ET.Element("AssetMap")
        root.attrib['xmlns'] = "http://www.smpte-ra.org/schemas/429-9/2007/AM"
        create_child_element(root, "Id", "urn:uuid:" + self.id)
        create_child_element(root, "AnnotationText", getattr(self, "annotation_text", "AAM Screener ASSETMAP " + self.id))
        create_child_element(root, "Creator", getattr(self, "creator", "AAM Screener"))
        create_child_element(root, "VolumeCount", getattr(self, "volume_index", "1"))
        create_child_element(root, "IssueDate", self.issue_date.strftime("%Y-%m-%dT%H:%M:%S%z"))
        create_child_element(root, "Issuer", getattr(self, 'issuer', "AAM Screener"))

        asset_list = ET.SubElement(root, "AssetList")
        for uuid, a in self.assets.iteritems():
            asset = ET.SubElement(asset_list, "Asset")
            create_child_element(asset, "Id", "urn:uuid:" + uuid)
            create_child_element(asset, "AnnotationText", getattr(a, 'annotation_text', 'AAM TMS - ASSETMAP: ' + uuid))

            # @todo: Add this element back in.
            # if f['type'] == "text/xml;asdcpKind=PKL":
            #     create_child_element(asset, "PackingList", "true")
            chunk_list = ET.SubElement(asset, "ChunkList")
            chunk = ET.SubElement(chunk_list, "Chunk")
            create_child_element(chunk, "Path", a.path)
            create_child_element(chunk, "VolumeIndex", getattr(a, "volume_index", "1"))
            create_child_element(chunk, "Offset", getattr(a, "offset", "0"))
            create_child_element(chunk, "Length", getattr(a, 'length', None))

        return ET.tostring(root, encoding="UTF-8")

    def __getitem__(self, k):
        return self.assets[k]

    def parse(self):
        """
        Parse the ASSETMAP. Extract the id, path, volume index, offset and
        length for each asset, and the validate the paths of the downloaded
        files against the paths from the ASSETMAP file.
        """
        try:
            self.validate()
        except Exception as e:
            raise AssetmapError(e)

        tree = ET.parse(self.path)
        root = tree.getroot()
        # ElementTree prepends the namespace to all elements, so we need to extract
        # it so that we can perform sensible searching on elements.
        assetmap_ns = get_namespace(root.tag)

        self.id = get_element_text(root, "Id", assetmap_ns).split(":")[2]
        self.annotation_text = get_element_text(root, "AnnotationText", assetmap_ns)
        self.volume_count = int(get_element_text(root, "VolumeCount", assetmap_ns))
        self.issue_date = parse_date(get_element_text(root, "IssueDate", assetmap_ns))
        self.issuer = get_element_text(root, "Issuer", assetmap_ns)
        self.creator = get_element_text(root, "Creator", assetmap_ns)

        asset_list = get_element(root, "AssetList", assetmap_ns)
        # Get the data from the ASSETMAP file
        for asset in asset_list.getchildren():
            asset_id = get_element_text(asset, "Id", assetmap_ns).split(":")[2]
            for chunklist in get_element_iterator(asset, "ChunkList", assetmap_ns):
                """
                The code below assumes that there will only ever be one chunk in a chunklist. Chunking is 
                used to split files up into smaller parts, usually in order to provide compatability with older
                filesystems, which is not applicable for our uses.
                """
                for chunk in chunklist.getchildren():
                    v = get_element_text(chunk, "VolumeIndex", assetmap_ns)
                    o = get_element_text(chunk, "Offset", assetmap_ns) 
                    l = get_element_text(chunk, "Length", assetmap_ns)
                    
                    a = {
                        "path": get_element_text(chunk, "Path", assetmap_ns),
                        "volume_index": int(v) if v is not None else v,
                        "offset": int(o) if o is not None else o,
                        "length": int(l) if l is not None else l
                    }

                    self.assets[asset_id] = AssetData(**a)
                    
    def validate(self, schema=os.path.join(os.path.dirname(__file__), 'am.xsd')):
        """
        Call the validate_xml function in util to validate the xml file against the schema.
        """
        return validate_xml(schema, self.path)

    def validate_files(self, dcp_path):
        """
        Check the paths of the downloaded files against the paths specified in the ASSETMAP file.
        """
        for asset_data in self.assets.itervalues():
            full_path = os.path.join(dcp_path, asset_data.path)
            if not os.path.isfile(full_path):
                raise AssetmapValidationError("File not found: {0}".format(full_path))


class AssetData(object):
    def __init__(self, path, volume_index, offset, length):
        self.path = path
        self.volume_index = volume_index
        self.offset = offset
        self.length = length
