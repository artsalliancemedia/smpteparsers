# from xml.etree import ElementTree
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from hashlib import sha1, md5, sha224, sha256, sha384, sha512
import base64

from smpteparsers.util import (get_element, get_element_text,
get_element_iterator, get_namespace)

class PKLError(Exception):
    pass
class PKLValidationError(PKLError):
    pass

class PKL(object):
    def __init__(self, path, assetmap):
        self.path = path
        self.assetmap = assetmap

        # A dictionary mapping uuids to PKLData objects containing the hash,
        # size and type of the asset
        self.assets = {}
        self.parse()

    def parse(self):
        """
        Parse the pkl.xml. Extract the id, hash, size and type for each asset,
        and then generate hashes for the downloaded files and validate them
        against the hashes from the pkl.xml file. (Note: only hashes for text
        files are checked
        """
        # Get hashes from pkl.xml file
        tree = ET.parse(self.path)
        root = tree.getroot()
        # Again, get the namespace so we can search elements
        pkl_ns = get_namespace(root.tag)

        asset_list = get_element(root, "AssetList", pkl_ns)
        assets = {}
        # Get the data from the pkl file
        for asset in asset_list.getchildren():
            asset_id = get_element_text(asset, "Id", pkl_ns)
            file_hash = get_element_text(asset, "Hash", pkl_ns)
            size = get_element_text(asset, "Size", pkl_ns)
            file_type = get_element_text(asset, "Type", pkl_ns)

            pkl_data = PKLData(file_hash, size, file_type)
            assets[asset_id] = pkl_data

        # Now that we've got the data from the pkl file, validate the hashes
        for uuid, pkl_data in assets.iteritems():
            full_path = os.path.join(self.assetmap.dcp_path,
                    self.assetmap.assets[uuid].path)
            if not full_path.endswith('.mxf') and pkl_data.file_hash != self.generate_hash(full_path):
                raise PKLValidationError("Hash doesn't match: {0}".format(full_path))

        self.assets = assets

    def generate_hash(self, local_path):
        """
        Work out the base64 encoded sha-1 hash of the file so we can compare
        integrity with hashes in pkl.xml file.

        Use 'chunking' in case we have to generate hashes for potentially very
        large .mxf files.
        """
        chunk_size = 1048576 # 1mb
        file_sha1 = sha1()
        with open("{0}".format(local_path), "r") as f:
            chunk = f.read(chunk_size)
            file_sha1.update(chunk)
            while chunk:
                chunk = f.read(chunk_size)
                file_sha1.update(chunk)
        file_hash = file_sha1.digest()
        encoded_hash = base64.b64encode(file_hash)
        return encoded_hash

class PKLData(object):
    def __init__(self, file_hash, size, file_type):
        self.file_hash = file_hash
        self.size = size
        self.file_type = file_type
