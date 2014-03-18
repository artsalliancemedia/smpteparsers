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
                'interop_kdm.xml'), 'r') as f:
            self.interop_kdm_xml = f.read()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                'smpte_kdm.xml'), 'r') as f:
            self.smpte_kdm_xml = f.read()

    def test_interop_from_string(self):
        kdm = KDM.from_string(self.interop_kdm_xml)
        self.assertEqual(kdm.id, 'fceeeb51-a60d-4771-bd23-5844d6a881ea')
        self.assertEqual(kdm.annotation_text,
            'XXX-YYY_FTR_F_EN-XX_UK-XX_51_2K_VTGO_20091029_AAM ~ KDM for LE SPB MD SM.DCP2000-204127.DC.DOLPHIN.CA.DOREMILABS.COM')
        self.assertEqual(kdm.issue_date, '2009-11-02T16:47:02+00:00')
        self.assertEqual(kdm.cpl_id, '91237d4e-be01-4711-afa9-c0b8809b4b4c')
        self.assertEqual(kdm.content_title_text, 'XXX-YYY_FTR_F_EN-XX_UK-XX_51_2K_VTGO_20091029_AAM')
        self.assertEqual(kdm.start_date, '2009-01-01T00:00:00+00:00')
        self.assertEqual(kdm.end_date, '2009-12-11T00:00:00+00:00')

    def test_smpte_from_string(self):
        kdm = KDM.from_string(self.smpte_kdm_xml)
        self.assertEqual(kdm.id, '6cfcdca2-2c0a-44eb-9df9-aadcf5491341')
        self.assertEqual(kdm.annotation_text,
            'XXX-YYY_FTR_F_EN-XX_UK_51_2K_MTRD_20120531_AAM_OV ~ KDM for SM SPB MDI MDA MDS FMI FMA.Dolby-CAT745-000000FC')
        self.assertEqual(kdm.issue_date, '2012-11-22T11:20:04+00:00')
        self.assertEqual(kdm.cpl_id, '85734a66-6786-4c86-98d0-b7f13b2af2b4')
        self.assertEqual(kdm.content_title_text, 'XXX-YYY_FTR_F_EN-XX_UK_51_2K_MTRD_20120531_AAM_OV')
        self.assertEqual(kdm.start_date, '2012-06-08T00:00:00+00:00')
        self.assertEqual(kdm.end_date, '2019-01-01T23:59:00+00:00')


if __name__ == '__main__':
    unittest.main()