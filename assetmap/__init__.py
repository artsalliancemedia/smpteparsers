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

        # A dictionary mapping uuids to AssetData objects containing the path,
        # volume index, offset and length of the asset
        self.assets = self.parse()

    def parse(self):
        """
        Parse the ASSETMAP. Extract the id, path, volume index, offset and
        length for each asset, and the validate the paths of the downloaded
        files against the paths from the ASSETMAP file.
        """
        # Get file paths from ASSETMAP FILE
        tree = ET.parse(self.path)
        root = tree.getroot()
        # ElementTree prepends the namespace to all elements, so we need to extract
        # it so that we can perform sensible searching on elements.
        right_brace = root.tag.rfind("}")
        assetmap_ns = root.tag[1:right_brace]

        asset_list = root.find("{0}{1}{2}AssetList".format("{", assetmap_ns,"}"))
        assets = {}
        # Get the data from the ASSETMAP file
        for asset in asset_list.getchildren():
            asset_id = asset.findtext("{0}{1}{2}Id".format("{", assetmap_ns,"}"))
            for chunklist in asset.getiterator("{0}{1}{2}ChunkList".format("{", assetmap_ns, "}")):
                for chunk in chunklist.getchildren():
                    path = chunk.findtext("{0}{1}{2}Path".format("{", assetmap_ns,"}"))
                    volume_index = chunk.findtext("{0}{1}{2}VolumeIndex".format("{", assetmap_ns,"}"))
                    offset = chunk.findtext("{0}{1}{2}Offset".format("{", assetmap_ns,"}"))
                    length = chunk.findtext("{0}{1}{2}Length".format("{", assetmap_ns,"}"))

                    asset_data = AssetData(path, volume_index, offset, length)
                    assets[asset_id] = asset_data

        # Now that we've got the data from the ASSETMAP file, validate the paths
        for asset_data in assets.itervalues():
            full_path = os.path.join(self.dcp_path, asset_data.path)
            if not os.path.isfile(full_path):
                logging.info("ERROR: File not found: {0}".format(full_path))
        else:
            logging.info("All file paths verified!")

        return assets

class AssetData(object):
    def __init__(self, path, volume_index, offset, length):
        self.path = path
        self.volume_index = volume_index
        self.offset = offset
        self.length = length
