import unittest
import json
from landowner.entities.instagram import ExifData

# -*- coding: utf-8 -*-


class TestExifData(unittest.TestCase):
    """Test cases for ExifData."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.exif_data = ExifData(
            latitude="12.34",
            longitude="56.78",
            iso="100",
            focal_length="50mm",
            lens_model="Sample Lens",
            scene_capture_type="Standard",
            software="Sample Software",
            device_id="Sample Device",
            scene_type="Sample Scene",
            camera_position="Sample Position",
            lens_make="Sample Make",
            date_time_digitized="2023-10-01T12:00:00Z",
            date_time_original="2023-10-01T12:00:00Z",
            source_type="Sample Source",
            aperture="f/1.8",
            shutter_speed="1/100s",
            metering_mode="Sample Mode"
        )

    def test_initialization(self):
        """Test the initialization of ExifData."""
        self.assertEqual(self.exif_data.latitude, "12.34")
        self.assertEqual(self.exif_data.longitude, "56.78")
        self.assertEqual(self.exif_data.iso, "100")
        self.assertEqual(self.exif_data.focal_length, "50mm")
        self.assertEqual(self.exif_data.lens_model, "Sample Lens")
        self.assertEqual(self.exif_data.scene_capture_type, "Standard")
        self.assertEqual(self.exif_data.software, "Sample Software")
        self.assertEqual(self.exif_data.device_id, "Sample Device")
        self.assertEqual(self.exif_data.scene_type, "Sample Scene")
        self.assertEqual(self.exif_data.camera_position, "Sample Position")
        self.assertEqual(self.exif_data.lens_make, "Sample Make")
        self.assertEqual(self.exif_data.date_time_digitized, "2023-10-01T12:00:00Z")
        self.assertEqual(self.exif_data.date_time_original, "2023-10-01T12:00:00Z")
        self.assertEqual(self.exif_data.source_type, "Sample Source")
        self.assertEqual(self.exif_data.aperture, "f/1.8")
        self.assertEqual(self.exif_data.shutter_speed, "1/100s")
        self.assertEqual(self.exif_data.metering_mode, "Sample Mode")

    def test_toJSON(self):
        """Test the toJSON method."""
        expected_json = json.dumps(
            self.exif_data,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4
        )
        self.assertEqual(self.exif_data.toJSON(), expected_json)

if __name__ == '__main__':
    unittest.main()