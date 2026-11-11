import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import collector

class CollectorTests(unittest.TestCase):
    def test_schema_does_not_claim_pass(self):
        data=collector.collect()
        self.assertEqual(data["kind"],"inventory_only")
        self.assertIsNone(data["health_verdict"])
        self.assertEqual(data["tests"],[])
        self.assertIsInstance(data["filesystems"],list)
        self.assertIsInstance(data["system"]["logical_cores"],(int,type(None)))
    def test_serializable(self):
        json.dumps(collector.collect())
    def test_missing_commands_do_not_crash(self):
        with patch.object(collector,"command",return_value=None):
            self.assertIsInstance(collector.memory(),dict)
if __name__=="__main__":unittest.main()
