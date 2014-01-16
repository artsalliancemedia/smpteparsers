class PlaylistError(Exception):
    pass
class PlaylistValidationError(PlaylistError):
    pass

class Playlist(object):
    def __init__(self, playlist_contents):
        pass

    def validate(self):
        # Perhaps look at JSON schema?
        raise NotImplementedError