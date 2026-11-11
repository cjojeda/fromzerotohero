import unittest
from unittest.mock import patch
import diagnostics

class DiagnosticsTests(unittest.TestCase):
    def test_checks_are_not_pass_verdicts(self):
        results=diagnostics.run_basic_checks()
        self.assertTrue(results)
        self.assertTrue(all(r["status"] in ("INFORMATIVO","ADVERTENCIA","NO DISPONIBLE") for r in results))
    def test_low_disk_warning(self):
        fake=type("Disk",(),{"total":100,"free":5})()
        with patch.object(diagnostics.shutil,"disk_usage",return_value=fake):
            self.assertEqual(diagnostics.run_basic_checks()[0]["status"],"ADVERTENCIA")
    def test_disk_unavailable(self):
        with patch.object(diagnostics.shutil,"disk_usage",side_effect=OSError("sin acceso")):
            self.assertEqual(diagnostics.run_basic_checks()[0]["status"],"NO DISPONIBLE")

if __name__=="__main__":unittest.main()
