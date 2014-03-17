import unittest
import os.path

from smpteparsers.kdm import KDM

class TestKDM(unittest.TestCase):
    """
    Tests KDM parsing functionality
    """

    def setUp(self):
        os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                'kdm.xml'), 'r') as f:
            self.kdm_xml = f.read()

    def test_parser(self):
        kdm = KDM.from_string(self.kdm_xml)
        self.assertEqual(kdm.id, 'fceeeb51-a60d-4771-bd23-5844d6a881ea')
        self.assertEqual(kdm.annotation_text,
            '1-DAY_FTR_F_EN-XX_UK-XX_51_2K_VTGO_20091029_AAM ~ KDM for LE SPB MD SM.DCP2000-204127.DC.DOLPHIN.CA.DOREMILABS.COM')
        self.assertEqual(kdm.issue_date, '2009-11-02T16:47:02+00:00')
        self.assertEqual(kdm.cpl_id, '91237d4e-be01-4711-afa9-c0b8809b4b4c')
        self.assertEqual(kdm.content_title_text, '1-DAY_FTR_F_EN-XX_UK-XX_51_2K_VTGO_20091029_AAM')
        self.assertEqual(kdm.start_date, '2009-01-01T00:00:00+00:00')
        self.assertEqual(kdm.end_date, '2009-12-11T00:00:00+00:00')


if __name__ == '__main__':
    unittest.main()