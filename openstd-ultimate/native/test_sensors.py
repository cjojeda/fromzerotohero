import unittest
from unittest.mock import patch
import sensors

class SensorTests(unittest.TestCase):
    def test_unavailable_windows_battery(self):
        with patch.object(sensors.platform,"system",return_value="Windows"),patch.object(sensors,"_ps",return_value=None):
            self.assertFalse(sensors.battery()["available"])
    def test_no_fabricated_windows_thermal(self):
        with patch.object(sensors.platform,"system",return_value="Windows"):
            result=sensors.thermal()
            self.assertFalse(result["available"])
            self.assertEqual(result["sensors"],[])
    def test_windows_disk_health_not_smart(self):
        with patch.object(sensors.platform,"system",return_value="Windows"),patch.object(sensors,"_ps",return_value={"FriendlyName":"Test","HealthStatus":"Healthy"}):
            result=sensors.disks()
            self.assertFalse(result["smart_attributes_available"])
            self.assertEqual(result["devices"][0]["health_status"],"Healthy")
    def test_snapshot_is_read_only(self):
        result=sensors.collect_sensors()
        self.assertEqual(result["kind"],"read_only_sensor_snapshot")
if __name__=="__main__":unittest.main()
