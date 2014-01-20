# from xml.etree import ElementTree
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

class CPLError(Exception):
    pass
class CPLValidationError(CPLError):
    pass

from smpteparsers.util import (get_element, get_element_text,
        get_element_iterator, get_namespace)
from time import strptime
import logging
from dateutil import parser

class CPL(object):
    def __init__(self, path):
        self.path = path
        self.cpl_id = ""
        self.metadata = {}
        self.reel_list = {}
        self.parse()

    def parse(self):
        '''
        Opens a given CPL asset, parses the XML to extract the playlist info and create a CPL object
        which is added to the DCP's CPL list.
        '''
        logging.info("Parsing CPL file...")

        tree = ET.parse(self.path)
        root = tree.getroot()
        # ElementTree prepends the namespace to all elements, so we need to extract
        # it so that we can perform sensible searching on elements.
        cpl_ns = get_namespace(root.tag)

        self.cpl_id = get_element_text(root, "Id", cpl_ns)
        # TODO Rating list. Not sure what it's supposed to look like, so not
        # sure how to parse it.
        
        # Get CPL metadata
        title = get_element_text(root, "ContentTitleText", cpl_ns)
        annotation = get_element_text(root, "AnnotationText", cpl_ns)
        issue_date_string = get_element_text(root, "IssueDate", cpl_ns)
        issue_date = parser.parse(issue_date_string)
        issuer = get_element_text(root, "Issuer", cpl_ns)
        creator = get_element_text(root, "Creator", cpl_ns)
        content_type = get_element_text(root, "ContentKind", cpl_ns)
        version_id = "urn:uri:{0}_{1}".format(self.cpl_id, issue_date_string)
        version_label = "{0}_{1}".format(self.cpl_id, issue_date_string)

        # Store CPL data in a dict
        self.metadata = {"title" : title,
                         "annotation" : annotation,
                         "issue_date" : issue_date,
                         "issuer" : issuer,
                         "creator" : creator,
                         "content_type" : content_type,
                         "version_id" : version_id,
                         "version_label" : version_label
                        }

        # Get the picture, sound and subtitle (if applicable) info
        tmp_reel_list = get_element(root, "ReelList", cpl_ns)
        for reel in tmp_reel_list.getchildren():
            reel_id = get_element_text(root, "Id", cpl_ns)
            for asset_list in get_element_iterator(reel, "AssetList", cpl_ns):
                # Get Main Picture metadata
                main_picture = get_element(asset_list, "MainPicture", cpl_ns)
                p_id = get_element_text(main_picture, "Id", cpl_ns)
                p_edit_rate = get_element_text(main_picture, "EditRate",
                        cpl_ns)
                p_intrinsic_duration = get_element_text(main_picture,
                    "IntrinsicDuration", cpl_ns)
                p_entry_point = get_element_text(main_picture,
                    "EntryPoint", cpl_ns)
                p_duration = get_element_text(main_picture, "Duration",
                        cpl_ns)
                p_frame_rate = get_element_text(main_picture, "FrameRate",
                        cpl_ns)
                p_screen_aspect_ratio = get_element_text(main_picture,
                    "ScreenAspectRatio", cpl_ns)

                picture = Picture(p_id, p_edit_rate, p_intrinsic_duration,
                        p_entry_point, p_duration, p_frame_rate,
                        p_screen_aspect_ratio)

                logging.info("Found Picture data.")

                # Get Main Sound metadata
                main_sound = get_element(asset_list, "MainSound", cpl_ns)
                s_id = get_element_text(main_sound, "Id", cpl_ns)
                s_edit_rate = get_element_text(main_sound, "EditRate",
                        cpl_ns)
                s_intrinsic_duration = get_element_text(main_sound,
                    "IntrinsicDuration", cpl_ns)
                s_entry_point = get_element_text(main_sound,
                    "EntryPoint", cpl_ns)
                s_duration = get_element_text(main_sound, "Duration",
                        cpl_ns)

                sound = Sound(s_id, s_edit_rate, s_intrinsic_duration,
                        s_entry_point, s_duration)

                logging.info("Found Sound data.")

                # There won't always be subtitle data, so first try and get the
                # MainSubstitle element...
                main_sub = get_element(asset_list, "MainSubtitle", cpl_ns)
                # ...and if it exists, get the subtitle data...
                if main_sub is not None:
                    sub_id = get_element_text(main_sub, "Id", cpl_ns)
                    sub_edit_rate = get_element_text(main_sub, "EditRate",
                            cpl_ns)
                    sub_intrinsic_duration = get_element_text(main_sub,
                        "IntrinsicDuration", cpl_ns)
                    sub_entry_point = get_element_text(main_sub,
                        "EntryPoint", cpl_ns)
                    sub_duration = get_element_text(main_sub, "Duration",
                            cpl_ns)
                    subtitle = Subtitle(sub_id, sub_edit_rate,
                            sub_intrinsic_duration, sub_entry_point, sub_duration)
                    logging.info("Found Subtitle data.")

                    reel = Reel(picture, sound, subtitle)
                # ...else there's no subtitle data, so just create a reel with
                # picture and sound info
                else:
                    reel = Reel(picture, sound)

                self.reel_list[reel_id] = reel

                logging.info("Finished parsing CPL file.")


    def validate(self):
        raise NotImplementedError


class Reel(object):
    def __init__(self, picture, sound, subtitle=None):
        self.picture = picture
        self.sound = sound
        self.subtitle = subtitle

    def __repr__(self):
        return 'Reel({0})'.format(self.id.split(':')[2])

class Picture(object):
    def __init__(self, pic_id, edit_rate, intrinsic_duration, entry_point,
                 duration, frame_rate, aspect_ratio, annotation=None):
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
    def __init__(self, sound_id, edit_rate, intrinsic_duration, entry_point,
                 duration, annotation=None, language=None):
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
    def __init__(self, sub_id, edit_rate, intrinsic_duration, entry_point,
                 duration, annotation=None, language=None):
        self.sub_id = sub_id
        self.edit_rate = tuple(edit_rate.split(' '))
        self.intrinsic_duration = int(intrinsic_duration)
        self.entry_point = int(entry_point)
        self.duration = int(duration)
        self.annotation = annotation
        self.language = language

    def __repr__(self):
        return 'Subtitle({0})'.format(self.sub_id.split(':')[2])


"""
class CPL(object):
    def __init__(self, path):
        self.dcp = dcp
        self.asset = asset
        self.id = id
        self.reel_list = reel_list
        self.rating_list = rating_list
        self.metadata = metadata

    def parse(self):
        '''
        Opens a given CPL asset, parses the XML to extract the playlist info and create a CPL object
        which is added to the DCP's CPL list.
        '''
        cpl_dom = dom.parse(os.path.join(self.dir, cpl_asset.filename))
        root = cpl_dom.getElementsByTagName('CompositionPlaylist')
        cpl_id = text_from_direct_child(root, 'Id')
        issue_date_string = text_from_direct_child(root, 'IssueDate')
        cpl = CPL(dcp=self,
                  asset=cpl_asset,
                  id=cpl_id,
                  metadata={'title': text_from_direct_child(root, 'ContentTitleText'),
                            'annotation': text_from_direct_child(root, 'AnnotationText'),
                            'issue_date': datetime.strptime(issue_date_string, "%Y-%m-%dT%H:%M:%S"),
                            'issuer': text_from_direct_child(root, 'Issuer'),
                            'creator': text_from_direct_child(root, 'Creator'),
                            'content_type': text_from_direct_child(root, 'ContentKind'),
                            'version_id': 'urn:uri:{0}_{1}'.format(cpl_id, issue_date_string),
                            'version_label': '{0}_{1}'.format(cpl_id, issue_date_string)})
      
        # fetch and parse reel info
        reels = root.getElementsByTagName('Reel')
        for reel_node in reels:
            reel_id = text_from_direct_child(reel_node, 'Id')
          
            # initialise the picture obj
            picture_node = reel_node.getElementsByTagName('MainPicture')[0]
            picture = Picture(cpl=cpl,
                              id=text_from_node(picture_node.getElementsByTagName('Id')),
                              edit_rate=text_from_node(picture_node.getElementsByTagName('EditRate')),
                              intrinsic_duration=text_from_node(picture_node.getElementsByTagName('IntrinsicDuration')),
                              entry_point=text_from_node(picture_node.getElementsByTagName('EntryPoint')),
                              duration=text_from_node(picture_node.getElementsByTagName('Duration')),
                              frame_rate=text_from_node(picture_node.getElementsByTagName('FrameRate')),
                              aspect_ratio=text_from_node(picture_node.getElementsByTagName('AspectRatio')),
                              annotation=text_from_node(picture_node.getElementsByTagName('AnnotationText')))
          
            # initialise the sound obj
            sound_node = reel_node.getElementsByTagName('MainSound')[0]
            sound = Sound(cpl=cpl,
                          id=text_from_node(sound_node.getElementsByTagName('Id')),
                          edit_rate=text_from_node(sound_node.getElementsByTagName('EditRate')),
                          intrinsic_duration=text_from_node(sound_node.getElementsByTagName('IntrinsicDuration')),
                          entry_point=text_from_node(sound_node.getElementsByTagName('EntryPoint')),
                          duration=text_from_node(sound_node.getElementsByTagName('Duration')),
                          annotation=text_from_node(sound_node.getElementsByTagName('AnnotationText')),
                          language=text_from_node(sound_node.getElementsByTagName('Language')))
          
            # finally initialise the reel
            reel = Reel(cpl=cpl,
                        id=reel_id,
                        picture=picture,
                        sound=sound)
            # and finally put the reel on the CPL reel_list
            cpl.reel_list.append(reel)
        return cpl

class Reel(object):
    def __init__(self, cpl, id, picture, sound):
        self.cpl = cpl
        self.id = id
        self.picture = picture
        self.sound = sound

    def __repr__(self):
        return 'Reel({0})'.format(self.id.split(':')[2])


class Picture(object):
    def __init__(self, cpl, id, edit_rate, intrinsic_duration, entry_point,
                 duration, frame_rate, aspect_ratio, annotation=None):
        self.cpl = cpl
        self.id = id
        self.asset = self.cpl.dcp.assets[self.id]
        self.edit_rate = tuple(edit_rate.split(' '))
        self.intrinsic_duration = int(intrinsic_duration)
        self.entry_point = int(entry_point)
        self.duration = int(duration)
        self.frame_rate = tuple(frame_rate.split(' '))
        self.aspect_ratio = float(aspect_ratio)
        self.annotation = annotation

    def __repr__(self):
        return 'Picture({0})'.format(self.id.split(':')[2])
  

class Sound(object):
    def __init__(self, cpl, id, edit_rate, intrinsic_duration, entry_point,
                 duration, annotation=None, language=None):
        self.cpl = cpl
        self.id = id
        self.asset = self.cpl.dcp.assets[self.id]
        self.annotation = annotation
        self.edit_rate = tuple(edit_rate.split(' '))
        self.intrinsic_duration = int(intrinsic_duration)
        self.entry_point = int(entry_point)
        self.duration = int(duration)
        self.language = language

    def __repr__(self):
        return 'Sound({0})'.format(self.id.split(':')[2])
"""
