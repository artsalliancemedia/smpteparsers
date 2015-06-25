import tarfile
import os.path

from kdm import KDM
from catalog import KDMBundleCatalog

class KDMBundle(object):
    """
    Manages SMPTE KDM bundles
    SMPTE Doc: S430-9-2008
    """

    def __init__(self, catalog, kdms):
        self.catalog = catalog
        self.kdms = kdms

    @classmethod
    def from_tarfile(cls, filepath):
        """
        Create a new KdmBundle instance from
        a KDM bundle tar file

        :param filepath: KDM bundle tar file
        :type filepath: string -- path to a tar file
        """
        tar = tarfile.open(filepath, 'r')
        # get the CATALOG xml doc
        cat_member = tar.getmember('CATALOG')
        catalog = KDMBundle._parse_catalog(tar.extractfile(cat_member).read())
        # get each of the referenced KDM files
        kdms = []
        for kdm_path in catalog.kdm_paths:
            # append the CONTENT root dir
            xml = tar.extractfile(os.path.join('CONTENT', kdm_path)).read()
            kdms.append(KDM(xml))
        tar.close()
        return cls(catalog, kdms)

    @staticmethod
    def _parse_catalog(xml_str):
        return KDMBundleCatalog.from_string(xml_str)

    def str(self, tar):
        for tarinfo in tar:
            print tarinfo.name, "is", tarinfo.size, "bytes in size and is",
            if tarinfo.isreg():
                print "a regular file."
            elif tarinfo.isdir():
                print "a directory."
            else:
                print "something else."

