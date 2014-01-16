# from xml.etree import ElementTree
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os, logging
from hashlib import sha1, md5, sha224, sha256, sha384, sha512
import base64

class PKL(object):
    def __init__(self, path, assetmap):
        self.path = path
        self.assetmap = assetmap

        self.ids_to_hashes = self.parse()

    def parse(self):
        # get hashes from pkl.xml file
        tree = ET.parse(self.path)
        root = tree.getroot()
        # Again, get the namespace so we can search elements
        right_brace = root.tag.rfind("}")
        pkl_ns = root.tag[1:right_brace]
        # Get all the hashes from the pkl files
        hashes = []
        for elem in root.getiterator("{0}{1}{2}Hash".format("{", pkl_ns, "}")):
            # print elem.text
            hashes.append(elem.text)
        # Get list of ids so we can match up entries in ASSETMAP to entries in pkl
        asset_list = root.find("{0}{1}{2}AssetList".format("{", pkl_ns,"}"))
        pkl_ids = []
        for elem in asset_list.getiterator("{0}{1}{2}Id".format("{", pkl_ns, "}")):
            pkl_ids.append(elem.text)
            

        ids_to_hashes = {}
        # Create a dict mapping ids to hashes that we can use later
        for pkl_id, filehash in zip(pkl_ids, hashes):
            ids_to_hashes[pkl_id] = filehash

        for pkl_id, file_hash in ids_to_hashes.items():
            full_path = self.assetmap.ids_to_paths[pkl_id]
            if not (full_path[-4:] == ".mxf" or file_hash == self.generate_hash(full_path)):
                logging.info("ERROR: Hash doesn't match: {0}".format(full_path))
        else:
            logging.info("All hashes verified!")
            
        return ids_to_hashes

    def generate_hash(self, local_path):
        """
        Work out the base64 encoded sha-1 hash of the file so we can compare
        integrity with hashes in pkl.xml file
        """
        chunk_size = 1048576 # 1mb
        file_sha1 = sha1()
        with open(r"{0}".format(local_path), "r") as f:
            chunk = f.read(chunk_size)
            file_sha1.update(chunk)
            while chunk:
                chunk = f.read(chunk_size)
                file_sha1.update(chunk)
        file_hash = file_sha1.digest()
        encoded_hash = base64.b64encode(file_hash)
        # logging.info("Hash for {0}: {1}".format(local_path, encoded_hash))
        return encoded_hash

