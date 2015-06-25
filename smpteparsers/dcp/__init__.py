import os
from smpteparsers.assetmap import Assetmap
from smpteparsers.pkl import PKL
from smpteparsers.cpl import CPL

class DCP(object):
    def __init__(self, path):
        self.path = path
        self.cpls = {}

        self.parse()

    def parse(self):
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

        self.assetmap = Assetmap(assetmap_path)
        self.pkl = PKL(pkl_path)

        """
        Find the CPL files using the pkl.xml and ASSETMAP files, then create a CPL
        object with the path to a CPL, which automatically parses the CPL file.
        """
        self.cpls = {}
        for uuid, pkl_data in self.pkl.assets.iteritems():
            if "asdcpKind=CPL" in pkl_data.file_type:
                cpl_path = os.path.join(self.path, self.assetmap[uuid].path)
                self.cpls[uuid] = CPL(cpl_path, assetmap=self.assetmap)

    def validate(self):
        raise NotImplementedError
        """
        Do file and hash validation here just for testing. Can/should be removed in future
        """
        # assetmap.validate_files(self.path)
        # pkl.validate_hashes(self.path, assetmap.assets)

