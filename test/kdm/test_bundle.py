import unittest
import os.path

from smpteparsers.kdm import KDMBundle

class TestKDMBundle(unittest.TestCase):
    """
    Tests KDM parsing functionality
    """

    def setUp(self):
        self.bundle_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bundle.tar')

    def test_from_tarfile(self):
        bundle = KDMBundle.from_tarfile(self.bundle_file)
        self.assertTrue(bundle.catalog)
        self.assertEqual(bundle.catalog.id, 'bundle')
        self.assertEqual(len(bundle.kdms), 3)
        self.assertEqual(bundle.kdms[0].id, 'f28aa57b-e3c9-4a56-861f-aed33fd3f70a')
        self.assertEqual(bundle.kdms[1].id, '6cfcdca2-2c0a-44eb-9df9-aadcf5491341')
        self.assertEqual(bundle.kdms[2].id, 'f0aa7325-3f90-4a3e-9d50-acd0f80d5c97')


if __name__ == '__main__':
    unittest.main()