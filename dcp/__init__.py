from smpteparsers import assetmap, pkl, cpl

class DCP(object):
    
    def __init__(self, path):
        self.path = path

        self.assets = self.parse_assets(self.path)
        self.cpls = self.parse_cpls()

    def parse_assets(self, path):
        '''
        Reads the Assetmap and then PKL file and ensures that all the transfers have been successful.
        '''

        # Delegate to the Assetmap and PKL parsers.

        pass

    def parse_cpls(self):
        # Use the list of assets generated in parse_assets to determine which ones are CPLs and therefore which ones to ingest.

        pass