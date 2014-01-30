# from xml.etree import ElementTree
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

"""
from smpteparsers.util import (get_element, get_element_text,
        get_element_iterator, get_namespace, validate_xml)
"""
import smpteparsers.util as util
from time import strptime
from dateutil import parser
import os, sys

class CPLError(Exception):
    pass
class CPLValidationError(CPLError):
    pass

schema_file = os.path.join(os.path.dirname(__file__), 'cpl.xsd') 

class CPL(object):
    def __init__(self, path, dcp_path=None, assetmap=None, check_xml=False):
        self.path = path
        self.dcp_path = dcp_path
        self.assetmap = assetmap
        self.check_xml = check_xml

        self.cpl_uuid = ""
        self.metadata = {}
        self.reels = []
        self.parse()

    def parse(self):
        """
        Opens a given CPL asset, parses the XML to extract the playlist info and create a CPL object
        which is added to the DCP's CPL list.
        """
        if self.check_xml:
            # TODO improve error handling code
            try:
                self.validate(schema_file, self.path)
            except Exception as e:
                print "CPLError: {0}".format(e)
                """
                There are currently bugs in the cpl.xsd file, which means all
                cpl xml files will fail validation. Therefore we only print the
                error here, but in reality we would want to raise an error as below.
                """
                # raise CPLError("CPLError: {0}".format(e))

        tree = ET.parse(self.path)
        root = tree.getroot()
        # ElementTree prepends the namespace to all elements, so we need to extract
        # it so that we can perform sensible searching on elements.
        cpl_ns = util.get_namespace(root.tag)

        self.cpl_uuid = util.get_element_text(root, "Id", cpl_ns).split(":")[2]
        # TODO Rating list. Not sure what it's supposed to look like, so not
        # sure how to parse it.
        
        # Check that we have somewhere to store CPL stuff
        # TODO Move path to config file
        ingest_folder = os.path.join(os.getcwd(), u'screener/INGEST')
        folder_path = util.check_directory(os.path.join(ingest_folder, self.cpl_uuid))
        #folder_path = util.check_directory(os.path.join("screener\INGEST", self.cpl_uuid))

        basename = os.path.basename(self.path)
        cpl_link_path = os.path.join(folder_path, basename)

        if not os.path.isfile(cpl_link_path):
            # TODO remove this after testing. catches the exception thrown
            # when a link has already been created.
            try:
                cpl_real_path = os.path.join(self.dcp_path, self.path)
                util.create_link(cpl_link_path, cpl_real_path)
            except:
                pass

        # Change self.path to point to link file
        self.path = cpl_link_path

        # Get CPL metadata
        self.metadata = self.get_metadata(root, cpl_ns)
        
        # Get the picture, sound and subtitle (if applicable) info
        tmp_reel_list = util.get_element(root, "ReelList", cpl_ns)
        for reel in tmp_reel_list.getchildren():
            reel_id = util.get_element_text(root, "Id", cpl_ns).split(":")[2]
            for asset_list in util.get_element_iterator(reel, "AssetList", cpl_ns):
                self.reels.append(Reel(reel_id, asset_list, cpl_ns, folder_path,
                    self.assetmap, self.dcp_path))

    def validate(self, schema_file, xml_file):
        """
        Call the validate_xml function in util to valide the xml file against
        the schema.
        """
        return util.validate_xml(schema_file, xml_file)

    def get_metadata(self, root, cpl_ns):
        title = util.get_element_text(root, "ContentTitleText", cpl_ns)
        annotation = util.get_element_text(root, "AnnotationText", cpl_ns)
        issue_date_string = util.get_element_text(root, "IssueDate", cpl_ns)
        issue_date = parser.parse(issue_date_string)
        issuer = util.get_element_text(root, "Issuer", cpl_ns)
        creator = util.get_element_text(root, "Creator", cpl_ns)
        content_type = util.get_element_text(root, "ContentKind", cpl_ns)
        version_id = "urn:uri:{0}_{1}".format(self.cpl_uuid, issue_date_string)
        version_label = "{0}_{1}".format(self.cpl_uuid, issue_date_string)

        # Store CPL data in a dict
        metadata = {
                        "title": title,
                        "annotation": annotation,
                        "issue_date": issue_date,
                        "issuer": issuer,
                        "creator": creator,
                        "content_type": content_type,
                        "version_id": version_id,
                        "version_label": version_label
                    }

        return metadata

class Reel(object):
    def __init__(self, reel_id, asset_list_el, cpl_ns, folder_path, assetmap,
            dcp_path):
        self.reel_id = reel_id
        
        pic_element = util.get_element(asset_list_el, "MainPicture", cpl_ns)
        self.picture = Picture(pic_element, cpl_ns, folder_path, assetmap,
                dcp_path)

        sound_element = util.get_element(asset_list_el, "MainSound", cpl_ns)
        self.sound = Sound(sound_element, cpl_ns, folder_path, assetmap,
                dcp_path)

        subt_element = util.get_element(asset_list_el, "MainSubtitle", cpl_ns)
        if subt_element is not None:
            self.subtitle = Subtitle(subt_element, cpl_ns, folder_path,
                    assetmap, dcp_path)

    def __repr__(self):
        return 'Reel({0})'.format(self.reel_id)

class Picture(object):
    def __init__(self, pic_element, cpl_ns, folder_path, assetmap, dcp_path):

        self.pic_id = util.get_element_text(pic_element, "Id", cpl_ns).split(":")[2]
        self.edit_rate = util.get_element_text(pic_element, "EditRate", cpl_ns)
        self.intrinsic_duration = util.get_element_text(pic_element, "IntrinsicDuration", cpl_ns)
        self.entry_point = util.get_element_text(pic_element, "EntryPoint", cpl_ns)
        self.duration = util.get_element_text(pic_element, "Duration", cpl_ns)
        self.frame_rate = util.get_element_text(pic_element, "FrameRate", cpl_ns)
        self.aspect_ration = util.get_element_text(pic_element, "ScreenAspectRatio", cpl_ns)

        # TODO Need a better way to get real path (i.e. path won't
        # necessarily always be id + file ext
        file_name = util.get_file_name(assetmap, folder_path, self.pic_id, ".mxf")

        link_path = os.path.abspath(os.path.join(folder_path, file_name))
        
        self.path = link_path

        if not os.path.isfile(link_path):
            # TODO remove this after testing. catches the exception thrown
            # when a link has already been created.
            try:
                real_path = os.path.join(dcp_path, file_name)
                util.create_link(link_path, real_path)
            except:
                pass

    def __repr__(self):
        return 'Picture({0})'.format(self.pic_id)

class Sound(object):
    def __init__(self, sound_element, cpl_ns, folder_path, assetmap, dcp_path):
        self.sound_id = util.get_element_text(sound_element, "Id", cpl_ns).split(":")[2]
        self.edit_rate = util.get_element_text(sound_element, "EditRate", cpl_ns)
        self.intrinsic_duration = util.get_element_text(sound_element, "IntrinsicDuration", cpl_ns)
        self.entry_point = util.get_element_text(sound_element, "EntryPoint", cpl_ns)
        self.duration = util.get_element_text(sound_element, "Duration", cpl_ns)
        self.frame_rate = util.get_element_text(sound_element, "FrameRate", cpl_ns)
        self.aspect_ration = util.get_element_text(sound_element, "ScreenAspectRatio", cpl_ns)

        # TODO Need a better way to get real path (i.e. path won't
        # necessarily always be id + file ext
        file_name = util.get_file_name(assetmap, folder_path, self.sound_id, ".mxf")

        link_path = os.path.join(folder_path, file_name)
        
        self.path = link_path

        if not os.path.isfile(link_path):
            # TODO remove this after testing. catches the exception thrown
            # when a link has already been created.
            try:
                real_path = os.path.join(dcp_path, file_name)
                util.create_link(link_path, real_path)
            except:
                pass

    def __repr__(self):
        return 'Sound({0})'.format(self.sound_id)

class Subtitle(object):
    def __init__(self, subt_element, cpl_ns, folder_path, assetmap, dcp_path):
        self.sub_id = util.get_element_text(subt_element, "Id", cpl_ns).split(":")[2]
        self.edit_rate = util.get_element_text(subt_element, "EditRate", cpl_ns)
        self.intrinsic_duration = util.get_element_text(subt_element, "IntrinsicDuration", cpl_ns)
        self.entry_point = util.get_element_text(subt_element, "EntryPoint", cpl_ns)
        self.duration = util.get_element_text(subt_element, "Duration", cpl_ns)

        # TODO Need a better way to get real path (i.e. path won't
        # necessarily always be id + file ext
        file_name = util.get_file_name(assetmap, folder_path, self.sub_id, ".xml")

        link_path = os.path.join(folder_path, file_name)
        
        self.path = link_path

        if not os.path.isfile(link_path):
            # TODO remove this after testing. catches the exception thrown
            # when a link has already been created.
            try:
                real_path = os.path.join(dcp_path, file_name)
                util.create_link(link_path, real_path)
            except:
                pass

    def __repr__(self):
        return 'Subtitle({0})'.format(self.sub_id.split(':')[2])
