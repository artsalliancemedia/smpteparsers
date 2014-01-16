from xml.etree import ElementTree

class CPL(object):
    pass

#     def __init__(self, path):
#         self.dcp = dcp
#         self.asset = asset
#         self.id = id
#         self.reel_list = reel_list
#         self.rating_list = rating_list
#         self.metadata = metadata

#     def parse(self):
#         '''
#         Opens a given CPL asset, parses the XML to extract the playlist info and create a CPL object
#         which is added to the DCP's CPL list.
#         '''
#         cpl_dom = dom.parse(os.path.join(self.dir, cpl_asset.filename))
#         root = cpl_dom.getElementsByTagName('CompositionPlaylist')
#         cpl_id = text_from_direct_child(root, 'Id')
#         issue_date_string = text_from_direct_child(root, 'IssueDate')
#         cpl = CPL(dcp=self,
#                   asset=cpl_asset,
#                   id=cpl_id,
#                   metadata={'title': text_from_direct_child(root, 'ContentTitleText'),
#                             'annotation': text_from_direct_child(root, 'AnnotationText'),
#                             'issue_date': datetime.strptime(issue_date_string, "%Y-%m-%dT%H:%M:%S"),
#                             'issuer': text_from_direct_child(root, 'Issuer'),
#                             'creator': text_from_direct_child(root, 'Creator'),
#                             'content_type': text_from_direct_child(root, 'ContentKind'),
#                             'version_id': 'urn:uri:{0}_{1}'.format(cpl_id, issue_date_string),
#                             'version_label': '{0}_{1}'.format(cpl_id, issue_date_string)})
        
#         # fetch and parse reel info
#         reels = root.getElementsByTagName('Reel')
#         for reel_node in reels:
#             reel_id = text_from_direct_child(reel_node, 'Id')
            
#             # initialise the picture obj
#             picture_node = reel_node.getElementsByTagName('MainPicture')[0]
#             picture = Picture(cpl=cpl,
#                               id=text_from_node(picture_node.getElementsByTagName('Id')),
#                               edit_rate=text_from_node(picture_node.getElementsByTagName('EditRate')),
#                               intrinsic_duration=text_from_node(picture_node.getElementsByTagName('IntrinsicDuration')),
#                               entry_point=text_from_node(picture_node.getElementsByTagName('EntryPoint')),
#                               duration=text_from_node(picture_node.getElementsByTagName('Duration')),
#                               frame_rate=text_from_node(picture_node.getElementsByTagName('FrameRate')),
#                               aspect_ratio=text_from_node(picture_node.getElementsByTagName('AspectRatio')),
#                               annotation=text_from_node(picture_node.getElementsByTagName('AnnotationText')))
            
#             # initialise the sound obj
#             sound_node = reel_node.getElementsByTagName('MainSound')[0]
#             sound = Sound(cpl=cpl,
#                           id=text_from_node(sound_node.getElementsByTagName('Id')),
#                           edit_rate=text_from_node(sound_node.getElementsByTagName('EditRate')),
#                           intrinsic_duration=text_from_node(sound_node.getElementsByTagName('IntrinsicDuration')),
#                           entry_point=text_from_node(sound_node.getElementsByTagName('EntryPoint')),
#                           duration=text_from_node(sound_node.getElementsByTagName('Duration')),
#                           annotation=text_from_node(sound_node.getElementsByTagName('AnnotationText')),
#                           language=text_from_node(sound_node.getElementsByTagName('Language')))
            
#             # finally initialise the reel
#             reel = Reel(cpl=cpl,
#                         id=reel_id,
#                         picture=picture,
#                         sound=sound)
#             # and finally put the reel on the CPL reel_list
#             cpl.reel_list.append(reel)
#         return cpl

# class Reel(object):
#     def __init__(self, cpl, id, picture, sound):
#         self.cpl = cpl
#         self.id = id
#         self.picture = picture
#         self.sound = sound

#     def __repr__(self):
#         return 'Reel({0})'.format(self.id.split(':')[2])


# class Picture(object):
#     def __init__(self, cpl, id, edit_rate, intrinsic_duration, entry_point,
#                  duration, frame_rate, aspect_ratio, annotation=None):
#         self.cpl = cpl
#         self.id = id
#         self.asset = self.cpl.dcp.assets[self.id]
#         self.edit_rate = tuple(edit_rate.split(' '))
#         self.intrinsic_duration = int(intrinsic_duration)
#         self.entry_point = int(entry_point)
#         self.duration = int(duration)
#         self.frame_rate = tuple(frame_rate.split(' '))
#         self.aspect_ratio = float(aspect_ratio)
#         self.annotation = annotation

#     def __repr__(self):
#         return 'Picture({0})'.format(self.id.split(':')[2])
    

# class Sound(object):
#     def __init__(self, cpl, id, edit_rate, intrinsic_duration, entry_point,
#                  duration, annotation=None, language=None):
#         self.cpl = cpl
#         self.id = id
#         self.asset = self.cpl.dcp.assets[self.id]
#         self.annotation = annotation
#         self.edit_rate = tuple(edit_rate.split(' '))
#         self.intrinsic_duration = int(intrinsic_duration)
#         self.entry_point = int(entry_point)
#         self.duration = int(duration)
#         self.language = language

#     def __repr__(self):
#         return 'Sound({0})'.format(self.id.split(':')[2])
