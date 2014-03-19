import unittest
import os.path

from smpteparsers.kdm import KDMBundleCatalog

class TestKDMBundleCatalog(unittest.TestCase):

    def setUp(self):
        os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                'catalog.xml'), 'r') as f:
            self.bundle_xml = f.read()

    def test_from_string(self):
        cat = KDMBundleCatalog.from_string(self.bundle_xml)
        self.assertEqual(cat.id, 'bundle')
        self.assertEqual(cat.annotation_text, 'Locksmith KDM Bundle')
        self.assertEqual(cat.creator, 'Arts Alliance Media Locksmith')
        self.assertEqual(cat.cpl_ids, [
            '1b347fec-9649-4c80-b53c-8e85d21562eb',
            '85734a66-6786-4c86-98d0-b7f13b2af2b4',
            '0b3dbeea-bffb-476c-8986-35ad8fd3a5df'
        ])
        self.assertEqual(cat.kdm_paths, [
            'KDM_f28aa57b-e3c9-4a56-861f-aed33fd3f70a.xml',
            'KDM_6cfcdca2-2c0a-44eb-9df9-aadcf5491341.xml',
            'KDM_f0aa7325-3f90-4a3e-9d50-acd0f80d5c97.xml'
        ])
        self.assertEqual(cat.start_dates, [
            '2012-03-12T00:00:00.000Z',
            '2012-06-08T00:00:00.000Z',
            '2012-06-13T00:00:00.000Z'
        ])
        self.assertEqual(cat.end_dates, [
            '2019-01-01T23:59:00.000Z',
            '2019-01-01T23:59:00.000Z',
            '2019-01-01T23:59:00.000Z'
        ])


if __name__ == '__main__':
    unittest.main()