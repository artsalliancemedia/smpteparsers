import unittest, json, re
from smpteparsers.playlist import Playlist, PlaylistValidationError

uuid_re = re.compile("^[a-fA-F\d]{8}-[a-fA-F\d]{4}-[a-fA-F\d]{4}-[a-fA-F\d]{4}-[a-fA-F\d]{12}$")
# Minimal info required for a playlist to be successful.
success_playlist = """
{
    "title": "Test playlist",
    "duration": 3600,
    "events": [
        {
            "cpl_id": "00000000-0000-0000-0000-100000000001",
            "type": "composition",
            "text": "Test CPL",
            "duration_in_frames": 43200,
            "duration_in_seconds": 1800,
            "edit_rate": [24, 1]
        },
        {
            "cpl_id": "00000000-0000-0000-0000-100000000002",
            "type": "composition",
            "text": "Test CPL 2",
            "duration_in_frames": 43200,
            "duration_in_seconds": 1800,
            "edit_rate": [24, 1]
        }
    ]
}
"""

class TestPlaylist(unittest.TestCase):
    def test_success(self):
        pl = Playlist()
        pl.parse(success_playlist)

        self.assertEqual(pl.title, "Test playlist")
        self.assertEqual(pl.duration, 3600)
        self.assertEqual(len(pl.events), 2)

        event0 = pl.events[0]
        self.assertEqual(event0.cpl_id, "00000000-0000-0000-0000-100000000001")
        self.assertEqual(event0.type, "composition")
        self.assertEqual(event0.text, "Test CPL")
        self.assertEqual(event0.duration_in_frames, 43200)
        self.assertEqual(event0.duration_in_seconds, 1800.0)
        self.assertEqual(event0.edit_rate[0], 24)
        self.assertEqual(event0.edit_rate[1], 1)

    def test_no_title(self):
        # Set up the data to start off with.
        err_playlist = json.loads(success_playlist)
        del(err_playlist["title"])

        pl = Playlist()
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Not a string
        err_playlist["title"] = 100
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Finally a successful test
        err_playlist["title"] = "Testing"
        pl.parse(err_playlist)

    def test_no_duration(self):
        # Set up the data to start off with.
        err_playlist = json.loads(success_playlist)
        del(err_playlist["duration"])

        pl = Playlist()
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Not an integer
        err_playlist["duration"] = "100"
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        err_playlist["duration"] = 100.1
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Finally a successful test
        err_playlist["duration"] = 100
        pl.parse(err_playlist)

    def test_no_events(self):
        # Set up the data to start off with.
        err_playlist = json.loads(success_playlist)
        err_playlist["events"] = []

        pl = Playlist()
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        del(err_playlist["events"])
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

    def test_event_cpl_uuid(self):
        # Set up the data to start off with.
        err_playlist = json.loads(success_playlist)
        err_playlist["events"][0]["cpl_id"] = None

        pl = Playlist()
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        err_playlist["events"][0]["cpl_id"] = "A string but not a valid uuid"
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Finally a successful test
        err_playlist["events"][0]["cpl_id"] = "00000000-0000-0000-0000-100000000001"
        pl.parse(err_playlist)

    def test_event_type(self):
        # Set up the data to start off with.
        err_playlist = json.loads(success_playlist)
        err_playlist["events"][0]["type"] = None

        pl = Playlist()
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        err_playlist["events"][0]["type"] = "not_a_composition"
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Finally a successful test
        err_playlist["events"][0]["type"] = "composition"
        pl.parse(err_playlist)

    def test_event_text(self):
        # Set up the data to start off with.
        err_playlist = json.loads(success_playlist)
        err_playlist["events"][0]["text"] = None

        pl = Playlist()
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Finally a successful test
        err_playlist["events"][0]["text"] = "Just some text"
        pl.parse(err_playlist)

    def test_event_duration_in_frames(self):
        # Set up the data to start off with.
        err_playlist = json.loads(success_playlist)
        err_playlist["events"][0]["duration_in_frames"] = None

        pl = Playlist()
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Only allow integer values.
        err_playlist["events"][0]["duration_in_frames"] = 100.1
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Finally a successful test
        err_playlist["events"][0]["duration_in_frames"] = 100
        pl.parse(err_playlist)

    def test_event_duration_in_seconds(self):
        # Set up the data to start off with.
        err_playlist = json.loads(success_playlist)
        err_playlist["events"][0]["duration_in_seconds"] = None

        pl = Playlist()
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Only allow integer values.
        err_playlist["events"][0]["duration_in_seconds"] = 100.1
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Finally a successful test
        err_playlist["events"][0]["duration_in_seconds"] = 100
        pl.parse(err_playlist)

    def test_event_edit_rate(self):
        # Set up the data to start off with.
        err_playlist = json.loads(success_playlist)
        err_playlist["events"][0]["edit_rate"] = []

        pl = Playlist()
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Must be exactly 2 integer values
        err_playlist["events"][0]["edit_rate"] = [100]
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)
        err_playlist["events"][0]["edit_rate"] = [100, 100, 100]
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Only allow integer values.
        err_playlist["events"][0]["edit_rate"] = [100.1, 100.1]
        self.assertRaises(PlaylistValidationError, pl.parse, err_playlist)

        # Finally a successful test
        err_playlist["events"][0]["edit_rate"] = [24, 1]
        pl.parse(err_playlist)

if __name__ == '__main__':
    unittest.main()
