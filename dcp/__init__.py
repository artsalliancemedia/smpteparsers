# from smpteparsers import assetmap, pkl, cpl
from smpteparsers.assetmap import Assetmap
from smpteparsers.pkl import PKL

import logging, os

class DCP(object):
    
    def __init__(self, path):
        self.path = path

        self.assets = self.parse_assets()
        self.cpls = self.parse_cpls()

    def parse_assets(self):
        '''
        Reads the Assetmap and then PKL file and ensures that all the transfers have been successful.
        '''
        
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

        # Delegate to the Assetmap and PKL parsers.


    def parse_cpls(self):
        # Use the list of assets generated in parse_assets to determine which ones are CPLs and therefore which ones to ingest.

        pass
