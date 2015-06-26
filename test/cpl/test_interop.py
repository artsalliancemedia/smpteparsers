import unittest, os, random
from datetime import datetime
from smpteparsers.cpl import CPL, CPLError

# Cannot use mock objects unfortunately, if we want to use cElementTree we cannot override "__builtin__.open" on that..
base_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'interop')
cpl_paths = {
    "success": os.path.join(base_data_path, 'success.xml'),

    "no_id": os.path.join(base_data_path, 'id', 'no_id.xml'),
    "invalid_id": os.path.join(base_data_path, 'id', 'invalid.xml'),

    "no_issue_date": os.path.join(base_data_path, 'issue_date', 'no_issue_date.xml'),
    "invalid_issue_date": os.path.join(base_data_path, 'issue_date', 'invalid.xml'),

    "no_content_title_text": os.path.join(base_data_path, 'no_content_title_text.xml'),
}

class TestCPL(unittest.TestCase):

    def assert_cpl_parsing(self, cpl):
        self.assertEqual(cpl.id, "649a5ca6-95d9-4dab-ad21-7636a636ca54")
        self.assertEqual(cpl.annotation_text, "Blenda Toeffere mot barneflekker 20130219_AAM_DCP")
        self.assertEqual(cpl.issue_date, datetime(2013, 2, 19, 15, 57, 55))
        self.assertEqual(cpl.issuer, "Arts Alliance Media")
        self.assertEqual(cpl.creator, "Arts Alliance Media - Bonaparte")
        self.assertEqual(cpl.content_title_text, "Blenda Toeffere mot barneflekker 20130219_AAM_DCP")
        self.assertEqual(cpl.content_kind, "advertisement")

        # Make sure we have the correct number of reels to start off with.
        self.assertEqual(len(cpl.reels), 1)

        reel = cpl.reels[0]
        self.assertEqual(reel.id, "68f63690-fdfc-41c0-a803-07a19ac88e6c")

        self.assertEqual(reel.picture.id, "fe3c6d6d-d36f-447b-aa19-af28955880bd")
        self.assertEqual(reel.picture.edit_rate, (24, 1))
        self.assertEqual(reel.picture.intrinsic_duration, 500)
        self.assertEqual(reel.picture.entry_point, 0)
        self.assertEqual(reel.picture.duration, 500)
        self.assertEqual(reel.picture.frame_rate, (24, 1))
        self.assertEqual(reel.picture.screen_aspect_ratio, (1998, 1080))

        self.assertEqual(reel.sound.id, "14d7b547-8b75-4df1-a126-5adebaead7dc")
        self.assertEqual(reel.sound.edit_rate, (24, 1))
        self.assertEqual(reel.sound.intrinsic_duration, 500)
        self.assertEqual(reel.sound.entry_point, 0)
        self.assertEqual(reel.sound.duration, 500)


    def test_success(self):
        cpl = CPL(cpl_paths["success"])
        self.assert_cpl_parsing(cpl)

    def test_success_string(self):
        cpl = CPL()
        with open(cpl_paths["success"]) as f:
            cpl.fromstring(f.read())
        self.assert_cpl_parsing(cpl)

    def test_id_fails(self):
        cpl = CPL(cpl_paths["no_id"], parse=False)
        self.assertRaises(CPLError, cpl.parse)

        cpl = CPL(cpl_paths["invalid_id"], parse=False)
        self.assertRaises(CPLError, cpl.parse)

    def test_issue_date_fails(self):
        cpl = CPL(cpl_paths["no_issue_date"], parse=False)
        self.assertRaises(CPLError, cpl.parse)

        cpl = CPL(cpl_paths["invalid_issue_date"], parse=False)
        self.assertRaises(CPLError, cpl.parse)

    def test_content_title_text_fails(self):
        cpl = CPL(cpl_paths["no_content_title_text"], parse=False)
        self.assertRaises(CPLError, cpl.parse)

if __name__ == '__main__':
    unittest.main()
