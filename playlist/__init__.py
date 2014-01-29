import os, json
from jsonschema import validate as validate_json
from jsonschema import ValidationError

"""
Not technically a SMPTE standard, just the format we use internally to represent a show playlist
within the TMS. Thought this was the best place for the parse alongside the others for easy discovery :)
"""

# Used to encapsulate the error so we don't expose we're using jsonschema.
class PlaylistValidationError(ValidationError):
    pass

class Playlist(object):
    def __init__(self, playlist_contents=None, parse=True, validate=True):
        """
        Init a new playlist to parse

        Args:
            playlist_contents (optional, default=None) - The contents of the playlist to parse
            parse (optional, default=True) - Whether to parse the contents immediately
            validate (optional, default=True) - Whether to validate the parsed contents immediately

        Returns:
            void
        """
        self.playlist_contents = playlist_contents

        if self.playlist_contents is not None and parse:
            self.parse(validate=validate)

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        # Override unicode to implement JSON serialisation.
        output = {
            "title": self.title,
            "duration": self.duration,
            "events": []
        }
        for event in self.events:
            output["events"].append(unicode(event))

        return json.dumps(output)

    def parse(self, playlist_contents=None, validate=True):
        """
        Parse a playlist dict

        Args:
            playlist_contents (optional, default=None) - The contents of the playlist to parse, if None 
                is received it'll try to load the existing playlist contents if there is some.
            validate (optional, default=True) - Whether to validate the parsed contents

        Returns:
            void
        """

        # Only update the playlist_contents if new contents are sent through otherwise take what was given in init()
        if playlist_contents is not None:
            self.playlist_contents = playlist_contents

        if type(self.playlist_contents) in [str, unicode]:
            try:
                self.playlist_contents = json.loads(self.playlist_contents)
            except ValueError:
                # Triggers if we send through something that isn't valid json
                self.playlist_contents = {}

        if validate:
            self.validate()

        # Now we've actually got a validate playlist dictionary lets parse this out into useful structures.
        self.title = self.playlist_contents['title']
        self.duration = self.playlist_contents['duration']

        self.events = []
        for event in self.playlist_contents['events']:
            self.events.append(PlaylistEvent(**event))

    def validate(self, schema_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'schema.json')):
        """
        Validate the playlist contents

        Args:
            schema_path (optional, default='./schema.json') - The path to the schema to validate the playlist against.

        Returns:
            void
        """
        with open(schema_path) as f:
            schema = json.load(f)

            try:
                validate_json(self.playlist_contents, schema)
            except ValidationError as e:
                # Encapsulate the error so we can hide the implementation to the client.
                raise PlaylistValidationError(e)

class PlaylistEvent(object):
    def __init__(self, cpl_id, type, text, duration_in_frames, duration_in_seconds, edit_rate):
        self.cpl_id = cpl_id
        self.type = type
        self.text = text
        self.duration_in_frames = duration_in_frames
        self.duration_in_seconds = duration_in_seconds
        self.edit_rate = edit_rate

    def __unicode__(self):
        fields = ("cpl_id", "type", "text", "duration_in_frames", "duration_in_seconds", "edit_rate")
        output = {}
        for field in fields:
            output[field] = getattr(self, field)

        return json.dumps(output)