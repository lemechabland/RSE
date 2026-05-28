"""Unit tests for the data store helpers."""

import tempfile
import unittest
from pathlib import Path

from ghg_manager.services.data_store import DataStore


class DataStoreTests(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "data.json"
            store = DataStore(path=path)
            sample = {"company": "Test Co", "activities": []}
            store.save(sample)
            loaded = store.load()
            self.assertEqual(sample, loaded)


if __name__ == "__main__":
    unittest.main()
