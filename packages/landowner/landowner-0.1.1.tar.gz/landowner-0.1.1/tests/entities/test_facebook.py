import unittest
from landowner.entities.facebook import Post, Tag, PostData, TextAttachment, Media, Place, Event, ExternalContext, ExifData

# -*- coding: utf-8 -*-


class TestFacebookEntities(unittest.TestCase):
    """Test cases for Facebook entities."""

    def test_post_initialization(self):
        post = Post(title="Sample Post", timestamp="2023-10-01T12:00:00Z")
        self.assertEqual(post.title, "Sample Post")
        self.assertEqual(post.timestamp, "2023-10-01T12:00:00Z")
        self.assertIsInstance(post.data, PostData)
        self.assertEqual(post.tags, [])
        self.assertEqual(post.attachments, [])

    def test_tag_initialization(self):
        tag = Tag(name="Sample Tag")
        self.assertEqual(tag.name, "Sample Tag")
        self.assertEqual(str(tag), "Sample Tag")

    def test_postdata_initialization(self):
        post_data = PostData(text="Sample Text", update_timestamp="2023-10-01T12:00:00Z")
        self.assertEqual(post_data.text, "Sample Text")
        self.assertEqual(post_data.update_timestamp, "2023-10-01T12:00:00Z")

    def test_textattachment_initialization(self):
        text_attachment = TextAttachment(text="Sample Attachment Text")
        self.assertEqual(text_attachment.text, "Sample Attachment Text")

    def test_media_initialization(self):
        media = Media(uri="sample_uri", title="Sample Title", description="Sample Description", timestamp="2023-10-01T12:00:00Z", exif_data="Sample Exif Data")
        self.assertEqual(media.uri, "sample_uri")
        self.assertEqual(media.title, "Sample Title")
        self.assertEqual(media.description, "Sample Description")
        self.assertEqual(media.timestamp, "2023-10-01T12:00:00Z")
        self.assertEqual(media.exif_data, "Sample Exif Data")

    def test_place_initialization(self):
        place = Place(latitude="12.34", longitude="56.78", name="Sample Place", address="Sample Address", url="http://sample.url")
        self.assertEqual(place.latitude, "12.34")
        self.assertEqual(place.longitude, "56.78")
        self.assertEqual(place.name, "Sample Place")
        self.assertEqual(place.address, "Sample Address")
        self.assertEqual(place.url, "http://sample.url")

    def test_event_initialization(self):
        event = Event(name="Sample Event", start_timestamp="2023-10-01T12:00:00Z", end_timestamp="2023-10-01T14:00:00Z", description="Sample Description", create_timestamp="2023-09-01T12:00:00Z", place="Sample Place")
        self.assertEqual(event.name, "Sample Event")
        self.assertEqual(event.start_timestamp, "2023-10-01T12:00:00Z")
        self.assertEqual(event.end_timestamp, "2023-10-01T14:00:00Z")
        self.assertEqual(event.description, "Sample Description")
        self.assertEqual(event.create_timestamp, "2023-09-01T12:00:00Z")
        self.assertEqual(event.place, "Sample Place")

    def test_externalcontext_initialization(self):
        external_context = ExternalContext(name="Sample Context", source="Sample Source", url="http://sample.url")
        self.assertEqual(external_context.name, "Sample Context")
        self.assertEqual(external_context.source, "Sample Source")
        self.assertEqual(external_context.url, "http://sample.url")

    def test_exifdata_initialization(self):
        exif_data = ExifData(
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
            metering_mode="Sample Mode",
            upload_ip="192.168.1.1",
            taken_timestamp="2023-10-01T12:00:00Z",
            orientation="Landscape"
        )
        self.assertEqual(exif_data.latitude, "12.34")
        self.assertEqual(exif_data.longitude, "56.78")
        self.assertEqual(exif_data.iso, "100")
        self.assertEqual(exif_data.focal_length, "50mm")
        self.assertEqual(exif_data.lens_model, "Sample Lens")
        self.assertEqual(exif_data.scene_capture_type, "Standard")
        self.assertEqual(exif_data.software, "Sample Software")
        self.assertEqual(exif_data.device_id, "Sample Device")
        self.assertEqual(exif_data.scene_type, "Sample Scene")
        self.assertEqual(exif_data.camera_position, "Sample Position")
        self.assertEqual(exif_data.lens_make, "Sample Make")
        self.assertEqual(exif_data.date_time_digitized, "2023-10-01T12:00:00Z")
        self.assertEqual(exif_data.date_time_original, "2023-10-01T12:00:00Z")
        self.assertEqual(exif_data.source_type, "Sample Source")
        self.assertEqual(exif_data.aperture, "f/1.8")
        self.assertEqual(exif_data.shutter_speed, "1/100s")
        self.assertEqual(exif_data.metering_mode, "Sample Mode")
        self.assertEqual(exif_data.upload_ip, "192.168.1.1")
        self.assertEqual(exif_data.taken_timestamp, "2023-10-01T12:00:00Z")
        self.assertEqual(exif_data.orientation, "Landscape")

if __name__ == '__main__':
    unittest.main()