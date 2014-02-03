from abc import ABCMeta
import os, sys
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from smpteparsers.util.date_utils import parse_date
from smpteparsers.util import get_element, get_element_text, get_element_iterator, get_namespace, validate_xml

class CPLError(Exception):
    pass
class CPLValidationError(CPLError):
    pass

class CPL(object):
    def __init__(self, path, assetmap=None):
        self.path = path
        self.assetmap = assetmap

        self.reels = []
        self.assets = {}

        self.parse()

    def parse(self):
        """
        Opens a given CPL asset, parses the XML to extract the playlist info and create a CPL object
        which is added to the DCP's CPL list.
        """
        try:
            self.validate()
        except Exception as e:
            raise CPLError(e)

        tree = ET.parse(self.path)
        root = tree.getroot()
        # ElementTree prepends the namespace to all elements, so we need to extract
        # it so that we can perform sensible searching on elements.
        cpl_ns = get_namespace(root.tag)

        self.id = get_element_text(root, "Id", cpl_ns).split(":")[2]
        self.title = get_element_text(root, "ContentTitleText", cpl_ns)
        self.annotation_text = get_element_text(root, "AnnotationText", cpl_ns)
        self.issue_date = parse_date(get_element_text(root, "IssueDate", cpl_ns))
        self.issuer = get_element_text(root, "Issuer", cpl_ns)
        self.creator = get_element_text(root, "Creator", cpl_ns)
        self.content_kind = get_element_text(root, "ContentKind", cpl_ns)

        # Get each of the parts of the CPL, i.e. the Reels :)
        for reel_list_elem in get_element_iterator(root, "ReelList", cpl_ns):
            for reel_elem in reel_list_elem.getchildren():
                reel = Reel(reel_elem, cpl_ns, assetmap=self.assetmap)

                # Add this in as a convenience for working with assets.
                for asset_id, asset in reel.assets.iteritems():
                    self.assets[asset_id] = asset

                self.reels.append(reel)

    def validate(self, schema=os.path.join(os.path.dirname(__file__), 'cpl.xsd')):
        """
        Call the validate_xml function in util to valide the xml file against the schema.
        """
        pass
        #return validate_xml(schema, self.path)

class Reel(object):
    def __init__(self, element, cpl_ns, assetmap=None):
        """
        Takes a "Reel" element and parses out the information contained inside.

        @todo: Check this against 3D content, in theory it should work but needs tests!
        """

        self.assets = {}
        self.id = get_element_text(element, "Id", cpl_ns).split(":")[2]

        for asset in get_element(element, "AssetList", cpl_ns).getchildren():
            asset_tag = asset.tag.split('}')[1] # Remove the namespace, hack but it works for now!
            if asset_tag in ("MainPicture", "MainStereoscopicPicture"):
                asset_instance = Picture(asset, cpl_ns)
                self.picture = asset_instance
            elif asset_tag == "MainSound":
                asset_instance = Sound(asset, cpl_ns)
                self.sound = asset_instance
            elif asset_tag == "MainSubtitle":
                asset_instance = Subtitle(asset, cpl_ns)
                self.subtitle = asset_instance
            else:
                raise CPLError("Unknown asset type found: {0}".format(asset_tag))

            # Finally set the path to this particular asset.
            if assetmap is not None:
                asset_instance.path = assetmap[asset_instance.id].path

            # Assets can be accessed in two ways now.
            self.assets[asset_instance.id] = asset_instance

class Asset(object):
    __metaclass__ = ABCMeta # Don't want Assets being defined on their own!

    def __init__(self, element, cpl_ns):
        self.id = get_element_text(element, "Id", cpl_ns).split(":")[2]
        self.edit_rate = get_element_text(element, "EditRate", cpl_ns)
        self.intrinsic_duration = get_element_text(element, "IntrinsicDuration", cpl_ns)
        self.entry_point = get_element_text(element, "EntryPoint", cpl_ns)
        self.duration = get_element_text(element, "Duration", cpl_ns)

class Picture(Asset):
    def __init__(self, element, cpl_ns):
        super(Picture, self).__init__(element, cpl_ns)

        self.frame_rate = get_element_text(element, "FrameRate", cpl_ns)
        self.aspect_ratio = get_element_text(element, "ScreenAspectRatio", cpl_ns)


class Sound(Asset):
    def __init__(self, element, cpl_ns):
        super(Sound, self).__init__(element, cpl_ns)

        self.frame_rate = get_element_text(element, "FrameRate", cpl_ns)
        self.aspect_ratio = get_element_text(element, "ScreenAspectRatio", cpl_ns)

class Subtitle(Asset):
    pass
