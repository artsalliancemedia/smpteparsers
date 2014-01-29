# from xml.etree import ElementTree
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from smpteparsers.util import (get_element, get_element_text,
        get_element_iterator, get_namespace, validate_xml)
from time import strptime
from dateutil import parser
import os, sys

class CPLError(Exception):
    pass
class CPLValidationError(CPLError):
    pass

schema_file = "screener/XSDs/cpl.xsd"

class CPL(object):
    def __init__(self, path, dcp_path=None, assetmap=None, check_xml=False):
        self.path = path
        self.dcp_path = dcp_path
        self.assetmap = assetmap
        self.check_xml = check_xml

        self.cpl_uuid = ""
        self.metadata = {}
        self.reels = {}
        self.parse()

    def parse(self):
        """
        Opens a given CPL asset, parses the XML to extract the playlist info and create a CPL object
        which is added to the DCP's CPL list.
        """
        if self.check_xml:
            # TODO improve error handling code
            try:
                self.xml_validate(schema_file, self.path)
            except Exception as e:
                pass
                # TODO Currently getting 'error parsing attribute name' error
                # here - no idea why
                # print e
                # raise CPLError("Error validating CPL XML")

        tree = ET.parse(self.path)
        root = tree.getroot()
        # ElementTree prepends the namespace to all elements, so we need to extract
        # it so that we can perform sensible searching on elements.
        cpl_ns = get_namespace(root.tag)

        self.cpl_uuid = get_element_text(root, "Id", cpl_ns).split(":")[2]
        # TODO Rating list. Not sure what it's supposed to look like, so not
        # sure how to parse it.
        
        # Check that we have somewhere to store CPL stuff
        local_path = ensure_local_path(self.cpl_uuid)

        cpl_link_path = os.path.join(local_path, self.path.split("\\")[-1])

        if not os.path.isfile(cpl_link_path):
            # TODO remove this after testing. catches the exception thrown
            # when a link has already been created.
            try:
                cpl_real_path = os.path.join(self.dcp_path, self.path)
                self.create_link(cpl_link_path, cpl_real_path)
            except:
                pass

        # Change self.path to point to link file
        self.path = cpl_link_path

        # Get CPL metadata
        self.metadata = self.get_metadata(root, cpl_ns)
        
        # Get the picture, sound and subtitle (if applicable) info
        tmp_reel_list = get_element(root, "ReelList", cpl_ns)
        for reel in tmp_reel_list.getchildren():
            reel_id = get_element_text(root, "Id", cpl_ns).split(":")[2]
            for asset_list in get_element_iterator(reel, "AssetList", cpl_ns):

                # Get Main Picture metadata
                main_picture = get_element(asset_list, "MainPicture", cpl_ns)
                picture = self.get_picture_data(main_picture, local_path, cpl_ns)

                # Get Main Sound metadata
                main_sound = get_element(asset_list, "MainSound", cpl_ns)
                sound = self.get_sound_data(main_sound, local_path, cpl_ns)

                # There won't always be subtitle data, so first try and get the
                # MainSubstitle element...
                main_sub = get_element(asset_list, "MainSubtitle", cpl_ns)
                # ...and if it exists, get the subtitle data...
                subtitle = self.get_subtitle_data(main_sub, local_path, cpl_ns) if main_sub is not None else None

                reel = Reel(picture, sound, subtitle)

                self.reels[reel_id] = reel


    def validate(self):
        raise NotImplementedError

    def xml_validate(self, schema_file, xml_file):
        """
        Call the validate_xml function in util to valide the xml file against
        the schema.
        """
        return validate_xml(schema_file, xml_file)

    def get_metadata(self, root, cpl_ns):
        title = get_element_text(root, "ContentTitleText", cpl_ns)
        annotation = get_element_text(root, "AnnotationText", cpl_ns)
        issue_date_string = get_element_text(root, "IssueDate", cpl_ns)
        issue_date = parser.parse(issue_date_string)
        issuer = get_element_text(root, "Issuer", cpl_ns)
        creator = get_element_text(root, "Creator", cpl_ns)
        content_type = get_element_text(root, "ContentKind", cpl_ns)
        version_id = "urn:uri:{0}_{1}".format(self.cpl_uuid, issue_date_string)
        version_label = "{0}_{1}".format(self.cpl_uuid, issue_date_string)

        # Store CPL data in a dict
        metadata = {
                        "title" : title,
                        "annotation" : annotation,
                        "issue_date" : issue_date,
                        "issuer" : issuer,
                        "creator" : creator,
                        "content_type" : content_type,
                        "version_id" : version_id,
                        "version_label" : version_label
                    }

        return metadata

    def get_picture_data(self, main_picture, local_path, cpl_ns):

        p = {
                "pic_id": get_element_text(main_picture, "Id", cpl_ns),
                "edit_rate": get_element_text(main_picture, "EditRate", cpl_ns),
                "intrinsic_duration": get_element_text(main_picture, "IntrinsicDuration", cpl_ns),
                "entry_point": get_element_text(main_picture, "EntryPoint", cpl_ns),
                "duration": get_element_text(main_picture, "Duration", cpl_ns),
                "frame_rate": get_element_text(main_picture, "FrameRate", cpl_ns),
                "aspect_ratio": get_element_text(main_picture, "ScreenAspectRatio", cpl_ns)
            }

        p_real_path = self.get_path(local_path, p["pic_id"], ".mxf")

        p_link_path = os.path.join(local_path, p_real_path)

        p["path"] = p_link_path

        if not os.path.isfile(p_link_path):
            # TODO remove this after testing. catches the exception thrown
            # when a link has already been created.
            try:
                p_real_path = os.path.join(self.dcp_path, p_real_path)
                self.create_link(p_link_path, p_real_path)
            except:
                pass

        picture = Picture(**p)
        
        return picture

    def get_sound_data(self, main_sound, local_path, cpl_ns):

        s = {
                "sound_id": get_element_text(main_sound, "Id", cpl_ns),
                "edit_rate": get_element_text(main_sound, "EditRate", cpl_ns),
                "intrinsic_duration": get_element_text(main_sound, "IntrinsicDuration", cpl_ns),
                "entry_point": get_element_text(main_sound, "EntryPoint", cpl_ns),
                "duration": get_element_text(main_sound, "Duration", cpl_ns),
            }

        s_real_path = self.get_path(local_path, s["sound_id"], ".mxf")

        s_link_path = os.path.join(local_path, s_real_path)

        s["path"] = s_link_path

        if not os.path.isfile(s_link_path):
            # TODO remove this after testing. catches the exception thrown
            # when a link has already been created.
            try:
                s_real_path = os.path.join(self.dcp_path, s_real_path)
                self.create_link(s_link_path, s_real_path)
            except:
                pass

        sound = Sound(**s)

        return sound
    
    def get_subtitle_data(self, main_sub, local_path, cpl_ns):

        sub = {
                "sub_id": get_element_text(main_sub, "Id", cpl_ns),
                "edit_rate": get_element_text(main_sub, "EditRate", cpl_ns),
                "intrinsic_duration": get_element_text(main_sub, "IntrinsicDuration", cpl_ns),
                "entry_point": get_element_text(main_sub, "EntryPoint", cpl_ns),
                "duration": get_element_text(main_sub, "Duration", cpl_ns),
                }

        sub_real_path = self.get_path(local_path, sub["sub_id"], ".xml")
        
        sub_link_path = os.path.join(local_path, sub_real_path)

        sub["path"] = sub_link_path

        if not os.path.isfile(sub_link_path):
            # TODO remove this after testing. catches the exception thrown
            # when a link has already been created.
            try:
                sub_real_path = os.path.join(self.dcp_path, sub_real_path)
                self.create_link(sub_link_path, sub_real_path)
            except:
                pass

        subtitle = Subtitle(**sub)

        return subtitle

    def get_path(self, dir_path, asset_id, file_ext):
        """
        Get the path for a file by first looking in the INGEST folder for a link
        file. If it is not found, look in ASSET 
        """
        search_path = asset_id.split(":")[2] + file_ext
        for root, dirs, files in os.walk(dir_path):
            for f in files:
                if f == search_path:
                    return os.path.join(root, f)
        else:
            return self.assetmap.assets[asset_id].path

    # Code taken from theatre/serv/cinema_services/lib/linking.py
    def create_link(self, hard_link_to, source_file):
        """
        Create a hardlink to a file. Should work on both Windows and Unix.
        """
        if sys.platform == 'win32':
            self.check_directory(hard_link_to)

            from ctypes import windll
            from ctypes.wintypes import BOOLEAN, LPWSTR, DWORD, LPVOID
            CreateHardLink = windll.kernel32.CreateHardLinkW
            CreateHardLink.argtypes = (LPWSTR, LPWSTR, LPVOID,)
            CreateHardLink.restype = BOOLEAN
            GetLastError = windll.kernel32.GetLastError
            GetLastError.argtypes = ()
            GetLastError.restype = DWORD

            error_dict = {
                    0: 'The operation completed successfully',
                    2: 'The system cannot find the file specified',
                    3: 'The system cannot find the path specified',
                    183: 'Cannot create a file when that file already exists',
                    1142: 'An attempt was made to create more links on a file than the file system supports'
            }

            if not CreateHardLink(hard_link_to, source_file, None):
                error_key = GetLastError()
                if error_key in error_dict:
                    error = error_dict[error_key]
                else:
                    error = 'ErrorKey[%s] not in Error_dict, goto http http://msdn.microsoft.com/en-us/library/ms681382(VS.85).aspx for description '% error_key
                error = error + '|| to: |' + str(hard_link_to) + '| source: |' + str(source_file) + '|'
                raise Exception(error)
        else:
            os.link(source_file, hard_link_to)

    def check_directory(self, file_path):
        """
        Check that the parent directories required for a file exist.
        If not, create them.
        """
        abs_path = os.path.abspath(file_path)

        parts = abs_path.split("\\")
        path = ""
        for part in parts[:-1]:
            path += part
            path += "\\"
            if not os.path.isdir(path):
                os.mkdir(path)

class Reel(object):
    def __init__(self, picture, sound, subtitle=None):
        self.picture = picture
        self.sound = sound
        self.subtitle = subtitle

    def __repr__(self):
        return 'Reel({0})'.format(self.id.split(':')[2])

class Picture(object):
    def __init__(self, path, pic_id, edit_rate, intrinsic_duration, entry_point,
                 duration, frame_rate, aspect_ratio, annotation=None):
        self.path = path
        self.pic_id = pic_id
        self.edit_rate = tuple(edit_rate.split(' '))
        self.intrinsic_duration = int(intrinsic_duration)
        self.entry_point = int(entry_point)
        self.duration = int(duration)
        self.frame_rate = tuple(frame_rate.split(' '))
        self.aspect_ratio = float(aspect_ratio)
        self.annotation = annotation

    def __repr__(self):
        return 'Picture({0})'.format(self.pic_id.split(':')[2])

class Sound(object):
    def __init__(self, path, sound_id, edit_rate, intrinsic_duration, entry_point,
                 duration, annotation=None, language=None):
        self.path = path
        self.sound_id = sound_id
        self.edit_rate = tuple(edit_rate.split(' '))
        self.intrinsic_duration = int(intrinsic_duration)
        self.entry_point = int(entry_point)
        self.duration = int(duration)
        self.annotation = annotation
        self.language = language

    def __repr__(self):
        return 'Sound({0})'.format(self.sound_id.split(':')[2])

class Subtitle(object):
    def __init__(self, path, sub_id, edit_rate, intrinsic_duration, entry_point,
                 duration, annotation=None, language=None):
        self.path = path
        self.sub_id = sub_id
        self.edit_rate = tuple(edit_rate.split(' '))
        self.intrinsic_duration = int(intrinsic_duration)
        self.entry_point = int(entry_point)
        self.duration = int(duration)
        self.annotation = annotation
        self.language = language

    def __repr__(self):
        return 'Subtitle({0})'.format(self.sub_id.split(':')[2])

def ensure_local_path(cpl_uuid):
    """
    Util function to ensure we have an INGEST folder to store CPL stuff in
    """
    # Just in case this is the first run, make sure we have the parent directory as well.
    # TODO, make cpl_store configurable
    cpl_store = os.path.join(os.getcwd(), u'screener\INGEST') 
    if not os.path.isdir(cpl_store):
        os.mkdir(cpl_store)

    local_path = os.path.join(cpl_store, cpl_uuid)
    if not os.path.isdir(local_path):
        os.mkdir(local_path) # Ensure we have a directory to download to.

    return local_path

