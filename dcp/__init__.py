# from smpteparsers import assetmap, pkl, cpl
from smpteparsers.assetmap import Assetmap
from smpteparsers.pkl import PKL
from smpteparsers.cpl import CPL

import logging, os

class DCP(object):
    
    def __init__(self, path):
        self.path = path

        self.assets = self.parse_assets()
        self.cpls = self.parse_cpls()

    def parse_assets(self):
        """
        Reads the Assetmap and then PKL file and ensures that all the transfers have been successful.
        """
        
        logging.info("Starting integrity verification...")

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
        assetmap = Assetmap(assetmap_path, self.path)
        pkl = PKL(pkl_path, assetmap)

        logging.info("Finished integrity verification")

        # Delegate to the Assetmap and PKL parsers.
        return {"pkl":pkl, "assetmap":assetmap}


    def parse_cpls(self):
        """
        Find the CPL files using the pkl.xml and ASSETMAP files, then create a CPL
        object with the path to a CPL, which automatically parses the CPL file.
        """
        # Use the list of assets generated in parse_assets to determine which ones are CPLs and therefore which ones to ingest.
        pkl = self.assets["pkl"]
        assetmap = self.assets["assetmap"]
       # TODO get list of all cpl files using Type tag from pkl, and Path tag
       # from ASSETMAP, matched on ID 

        cpl_uuids = []
        for uuid, pkl_data in pkl.assets.iteritems():
            if pkl_data.file_type == "text/xml;asdcpKind=CPL":
                cpl_uuids.append(uuid)

        cpl_paths = {}
        for cpl_uuid in cpl_uuids:
            cpl_paths[cpl_uuid] = os.path.join(self.path,
                    assetmap.assets[cpl_uuid].path)
        
        cpls = {}
        for cpl_uuid, cpl_path in cpl_paths.iteritems():
            cpl = CPL(cpl_path) 
            cpls[cpl_uuid] = cpl

        return cpls
        
