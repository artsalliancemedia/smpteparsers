import unittest, os, random
from datetime import datetime
from smpteparsers.assetmap import Assetmap, AssetmapError

# Cannot use mock objects unfortunately, if we want to use cElementTree we cannot override "__builtin__.open" on that..
base_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
am_paths = {
    "success": os.path.join(base_data_path, 'success.xml'),

    "no_id": os.path.join(base_data_path, 'id', 'no_id.xml'),
    "invalid_id": os.path.join(base_data_path, 'id', 'invalid.xml'),

    "no_volume_count": os.path.join(base_data_path, 'volume_count', 'no_volume_count.xml'),
    "negative_volume_count": os.path.join(base_data_path, 'volume_count', 'negative.xml'),
    "string_volume_count": os.path.join(base_data_path, 'volume_count', 'string.xml'),

    "no_issue_date": os.path.join(base_data_path, 'issue_date', 'no_issue_date.xml'),
    "invalid_issue_date": os.path.join(base_data_path, 'issue_date', 'invalid.xml'),

    "no_issuer": os.path.join(base_data_path, 'no_issuer.xml'),
    "no_creator": os.path.join(base_data_path, 'no_creator.xml'),

    "no_assets": os.path.join(base_data_path, 'assets', 'no_assets.xml'),
    "no_asset_id": os.path.join(base_data_path, 'assets', 'no_asset_id.xml'),
    "invalid_asset_id": os.path.join(base_data_path, 'assets', 'invalid_asset_id.xml'),

    "no_chunks": os.path.join(base_data_path, 'assets', 'no_chunks.xml'),
    "no_chunk_path": os.path.join(base_data_path, 'assets', 'no_chunk_path.xml')
}

class TestAssetmap(unittest.TestCase):
    def test_success(self):
        am = Assetmap(am_paths["success"])

        self.assertEqual(am.id, "aea7e1f1-aa1b-4467-9002-2ff11e0f3669")
        self.assertEqual(am.annotation_text, "TMS ASSETMAP - aea7e1f1-aa1b-4467-9002-2ff11e0f3669")
        self.assertEqual(am.volume_count, 1)
        self.assertEqual(am.issue_date, datetime(2013, 5, 28, 10, 47, 8)) # This may need tzinfo to actually work :)
        self.assertEqual(am.issuer, "Arts Alliance Media")
        self.assertEqual(am.creator, "TMS")

        success_asset_ids = set(["01658edd-edfb-4c52-beec-1f5b9616e813", "7ec59b28-8ef4-4963-88e8-9d0a08763b4a"])

        # Make sure we got all the assets processed.
        self.assertEqual(len(am.assets.keys()), 2)
        self.assertEqual(set(am.assets.keys()), success_asset_ids)

        # Just test one asset, that's be enough for us
        asset = am.assets["01658edd-edfb-4c52-beec-1f5b9616e813"]
        self.assertEqual(asset.path, "01658edd-edfb-4c52-beec-1f5b9616e813.xml")
        self.assertEqual(asset.volume_index, 1)
        self.assertEqual(asset.offset, 0)
        self.assertEqual(asset.length, 8075)

    def test_id_fails(self):
        am = Assetmap(am_paths["no_id"], parse=False)
        self.assertRaises(AssetmapError, am.parse)

        am = Assetmap(am_paths["invalid_id"], parse=False)
        self.assertRaises(AssetmapError, am.parse)

    def test_volume_count_fails(self):
        am = Assetmap(am_paths["no_volume_count"], parse=False)
        self.assertRaises(AssetmapError, am.parse)

        am = Assetmap(am_paths["negative_volume_count"], parse=False)
        self.assertRaises(AssetmapError, am.parse)

        am = Assetmap(am_paths["string_volume_count"], parse=False)
        self.assertRaises(AssetmapError, am.parse)

    def test_issue_date_fails(self):
        am = Assetmap(am_paths["no_issue_date"], parse=False)
        self.assertRaises(AssetmapError, am.parse)

        am = Assetmap(am_paths["invalid_issue_date"], parse=False)
        self.assertRaises(AssetmapError, am.parse)

    def test_issuer_fails(self):
        am = Assetmap(am_paths["no_issuer"], parse=False)
        self.assertRaises(AssetmapError, am.parse)

    def test_creator_fails(self):
        am = Assetmap(am_paths["no_creator"], parse=False)
        self.assertRaises(AssetmapError, am.parse)

    def test_assets_fails(self):
        am = Assetmap(am_paths["no_assets"], parse=False)
        self.assertRaises(AssetmapError, am.parse)

    def test_asset_id_fails(self):
        am = Assetmap(am_paths["no_asset_id"], parse=False)
        self.assertRaises(AssetmapError, am.parse)

    def test_chunks_fails(self):
        am = Assetmap(am_paths["no_chunks"], parse=False)
        self.assertRaises(AssetmapError, am.parse)

    def test_chunk_path_fails(self):
        am = Assetmap(am_paths["no_chunk_path"], parse=False)
        self.assertRaises(AssetmapError, am.parse)


if __name__ == '__main__':
    unittest.main()
