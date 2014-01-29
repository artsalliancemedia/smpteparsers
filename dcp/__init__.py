# from smpteparsers import assetmap, pkl, cpl
from smpteparsers.assetmap import Assetmap
from smpteparsers.pkl import PKL
from smpteparsers.cpl import CPL

import os

class DCP(object):
    
    def __init__(self, path):
        self.path = path

        self.parse_assets()
        self.cpls = {}
        self.parse_cpls()

    def parse_assets(self):
        """
        Reads the Assetmap and then PKL file and ensures that all the transfers have been successful.
        """
        assetmap_path = ""
        assetmap_found = False
        pkl_path = ""
        pkl_found = False

        for root, dirs, files in os.walk(self.path):
            for f in files:
                if "assetmap" in f.lower():
                    assetmap_path = os.path.join(root, f)
                    assetmap_found = True
                elif "pkl.xml" in f.lower():
                    pkl_path = os.path.join(root, f)
                    pkl_found = True
                if assetmap_found and pkl_found:
                    break
        assetmap = Assetmap(assetmap_path, self.path, True)
        pkl = PKL(pkl_path, assetmap, True)


        # Delegate to the Assetmap and PKL parsers.
        self.pkl = pkl
        self.assetmap = assetmap


    def parse_cpls(self):
        """
        Find the CPL files using the pkl.xml and ASSETMAP files, then create a CPL
        object with the path to a CPL, which automatically parses the CPL file.
        """
        # Use the list of assets generated in parse_assets to determine which ones are CPLs and therefore which ones to ingest.
        cpl_uuids = []
        for uuid, pkl_data in self.pkl.assets.iteritems():
            if "asdcpKind=CPL" in pkl_data.file_type:
                cpl_uuids.append(uuid)

        cpl_paths = {}
        for cpl_uuid in cpl_uuids:
            cpl_paths[cpl_uuid] = os.path.join(self.path,
                    self.assetmap.assets[cpl_uuid].path)
        
        cpls = {}
        for cpl_uuid, cpl_path in cpl_paths.iteritems():
            cpl = CPL(cpl_path, self.path, self.assetmap, True) 
            cpls[cpl_uuid] = cpl

        self.cpls = cpls
