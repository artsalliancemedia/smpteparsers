# from xml.etree import ElementTree
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os, logging


class Assetmap(object):
    def __init__(self, path, dcp_path):
        self.path = path
        self.dcp_path = dcp_path

        self.ids_to_paths = self.parse()

    def parse(self):
        # get file paths from ASSETMAP FILE
        tree = ET.parse(self.path)
        root = tree.getroot()
        # ElementTree prepends the namespace to all elements, so we need to extract
        # it so that we can perform sensible searching on elements.
        right_brace = root.tag.rfind("}")
        assetmap_ns = root.tag[1:right_brace]
        file_paths = []
        # Get all file paths in the ASSETMAP file
        for elem in root.getiterator("{0}{1}{2}Path".format("{", assetmap_ns, "}")):
            # print elem.text
            file_paths.append(elem.text)
        # Get list of ids so we can match up entries in ASSETMAP to entries in
        # pkl later if required
        asset_list = root.find("{0}{1}{2}AssetList".format("{", assetmap_ns,"}"))
        assetmap_ids = []
        for elem in asset_list.getiterator("{0}{1}{2}Id".format("{", assetmap_ns, "}")):
            assetmap_ids.append(elem.text)
            
        full_paths = []
        for file_path in file_paths:
            full_path = os.path.join(self.dcp_path, file_path)
            if not os.path.isfile(full_path):
                logging.info("ERROR: File not found: {0}".format(full_path))
            else:
                full_paths.append(full_path)
        else:
            logging.info("All file paths verified!")

        # Create a dict mapping ids to paths that we can use later
        ids_to_paths = {}
        for assetmap_id, full_path in zip(assetmap_ids, full_paths):
            ids_to_paths[assetmap_id] = full_path

        return ids_to_paths
