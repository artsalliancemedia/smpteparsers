import os, base64, hashlib
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from smpteparsers.util import get_element, get_element_text, get_element_iterator, get_namespace, validate_xml

class PKLError(Exception):
    pass
class PKLValidationError(PKLError):
    pass

class PKL(object):
    def __init__(self, path):
        self.path = path

        # Stores the assets info, most importantly the hash, size and file type.
        self.assets = {}

        self.parse()

    def parse(self):
        """
        Parse the pkl.xml, extracts asset info for storage in memory.
        """
        try:
            self.validate()
        except Exception as e:
            raise PKLError(e)

        # Get hashes from pkl.xml file
        tree = ET.parse(self.path)
        root = tree.getroot()

        # Again, get the namespace so we can search elements
        pkl_ns = get_namespace(root.tag)
        self.id = get_element_text(root, "Id", pkl_ns).split(":")[2]

        asset_list = get_element(root, "AssetList", pkl_ns)

        # Get the data from the pkl file
        for asset in asset_list.getchildren():
            asset_id = get_element_text(asset, "Id", pkl_ns).split(":")[2]

            p = {
                "file_hash": get_element_text(asset, "Hash", pkl_ns),
                "size": get_element_text(asset, "Size", pkl_ns),
                "file_type": get_element_text(asset, "Type", pkl_ns)
            }

            self.assets[asset_id] = PKLData(**p)

    def validate(self, schema=os.path.join(os.path.dirname(__file__), 'pkl.xsd')):
        """
        Call the validate_xml function in util to validate the xml file against the schema.
        """
        pass
        #return validate_xml(schema, self.path)

    def validate_hashes(self, dcp_path, assets):
        """
        Generate hashes for local files, and validate them against the hashes in the pkl file.
        
        Note: Currently not checking hashes for binary (.mxf) files.
        """
        for uuid, pkl_data in self.assets.iteritems():
            full_path = os.path.join(dcp_path, assets[uuid].path)

            # Skip MXF files for now, we will add in support for this later on.
            if full_path.endswith('.mxf'):
                continue

            if pkl_data.file_hash != generate_hash(full_path):
                raise PKLValidationError("Hash doesn't match: {0}".format(full_path))

class PKLData(object):
    def __init__(self, file_hash, size, file_type):
        self.file_hash = file_hash
        self.size = size
        self.file_type = file_type

def generate_hash(local_path):
    """
    Work out the base64 encoded sha-1 hash of the file so we can compare integrity with hashes in pkl.xml file.
    Use 'chunking' in case we have to generate hashes for potentially very large .mxf files.
    """
    chunk_size = 1048576 # 1mb
    file_sha1 = hashlib.sha1()
    with open(local_path) as f:
        chunk = f.read(chunk_size)
        while chunk:
            file_sha1.update(chunk)
            chunk = f.read(chunk_size)

    return base64.b64encode(file_sha1.digest())
