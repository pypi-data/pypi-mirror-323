# -*- coding: utf-8 -*-
import unittest
from landowner.deserializers.facebook import FacebookPostExportDeserializer
from landowner.entities import facebook as Facebook

class TestFacebookPostExportDeserializer(unittest.TestCase):

    def setUp(self):
        self.deserializer = FacebookPostExportDeserializer()

    def test_extract_event_attachment(self):
        event_dict = {
            "name": "Birthday Party",
            "place": {
                "name": "John's House",
                "coordinate": {
                    "latitude": 40.7128,
                    "longitude": -74.0060
                }
            }
        }
        event = self.deserializer._extract_event_attachment(event_dict)
        self.assertEqual(event.name, "Birthday Party")
        self.assertEqual(event.place.name, "John's House")
        self.assertEqual(event.place.latitude, 40.7128)
        self.assertEqual(event.place.longitude, -74.0060)

    def test_extract_external_context_attachment(self):
        external_context_dict = {
            "url": "http://example.com",
            "name": "Example Title",
            "source": "Example Source"
        }
        external_context = self.deserializer._extract_external_context_attachment(external_context_dict)
        self.assertEqual(external_context.url, "http://example.com")
        self.assertEqual(external_context.name, "Example Title")
        self.assertEqual(external_context.source, "Example Source")

    def test_extract_media_attachment(self):
        media_dict = {
            "uri": "http://example.com/image.jpg",
            "title": "Example Image",
            "description": "An example image",
            "creation_timestamp": 1609459200,
            "media_metadata": {
                "photo_metadata": {
                    "exif_data": [
                        {"orientation": "Portrait", "device_id": "EOS 80D"}
                    ]
                }
            }
        }
        media = self.deserializer._extract_media_attachment(media_dict)
        self.assertEqual(media.uri, "http://example.com/image.jpg")
        self.assertEqual(media.title, "Example Image")
        self.assertEqual(media.description, "An example image")
        self.assertEqual(media.timestamp, 1609459200)
        self.assertEqual(media.exif_data.orientation, "Portrait")
        self.assertEqual(media.exif_data.device_id, "EOS 80D")

    def test_extract_post_data(self):
        data_list = [
            {"post": "Hello World!", "update_timestamp": 1609459200}
        ]
        post_data = self.deserializer._extract_post_data(data_list)
        self.assertEqual(post_data.text, "Hello World!")
        self.assertEqual(post_data.update_timestamp, 1609459200)

    def test_extract_place_attachment(self):
        place_dict = {
            "name": "Central Park",
            "address": "New York, NY",
            "url": "http://example.com",
            "coordinate": {
                "latitude": 40.785091,
                "longitude": -73.968285
            }
        }
        place = self.deserializer._extract_place_attachment(place_dict)
        self.assertEqual(place.name, "Central Park")
        self.assertEqual(place.address, "New York, NY")
        self.assertEqual(place.url, "http://example.com")
        self.assertEqual(place.latitude, 40.785091)
        self.assertEqual(place.longitude, -73.968285)

    def test_extract_text_attachment(self):
        attachment_data_item = {"text": "Sample text"}
        text_attachment = self.deserializer._extract_text_attachment(attachment_data_item)
        self.assertEqual(text_attachment.text, "Sample text")

    def test_sanitize_string_value(self):
        value = "Café"
        sanitized_value = self.deserializer._sanitize_string_value(value)
        self.assertEqual(sanitized_value, "Café")

    def test_sanitize_string_value_with_mojibake(self):
        value = "CafÃ©"
        sanitized_value = self.deserializer._sanitize_string_value(value)
        self.assertEqual(sanitized_value, "Café")

    def test_sanitize_string_value_with_special_characters(self):
        value = "Café & Restaurant"
        sanitized_value = self.deserializer._sanitize_string_value(value)
        self.assertEqual(sanitized_value, "Café & Restaurant")

    def test_sanitize_string_value_with_unicode(self):
        value = "こんにちは"
        sanitized_value = self.deserializer._sanitize_string_value(value)
        self.assertEqual(sanitized_value, "こんにちは")

    def test_sanitize_string_value_with_empty_string(self):
        value = ""
        sanitized_value = self.deserializer._sanitize_string_value(value)
        self.assertEqual(sanitized_value, "")

    def test_deserialize(self):
        data = [
            {
                "title": "Sample Post",
                "timestamp": 1609459200,
                "data": [{"post": "Hello World!", "update_timestamp": 1609459200}],
                "tags": [{"name": "tag1"}],
                "attachments": [
                    {
                        "data": [
                            {"text": "Sample text"},
                            {"media": {"uri": "http://example.com/image.jpg", "title": "Example Image", "description": "An example image", "creation_timestamp": 1609459200}},
                            {"place": {"name": "Central Park", "address": "New York, NY", "url": "http://example.com", "coordinate": {"latitude": 40.785091, "longitude": -73.968285}}},
                            {"event": {"name": "Birthday Party", "place": {"name": "John's House", "coordinate": {"latitude": 40.7128, "longitude": -74.0060}}}},
                            {"external_context": {"url": "http://example.com", "title": "Example Title"}}
                        ]
                    }
                ]
            }
        ]
        posts = self.deserializer.deserialize(data)
        self.assertEqual(len(posts), 1)
        post = posts[0]
        self.assertEqual(post.title, "Sample Post")
        self.assertEqual(post.timestamp, 1609459200)
        self.assertEqual(post.data.text, "Hello World!")
        self.assertEqual(post.data.update_timestamp, 1609459200)
        self.assertEqual(len(post.tags), 1)
        self.assertEqual(post.tags[0].name, "tag1")
        self.assertEqual(len(post.attachments), 5)
        self.assertEqual(post.attachments[0].text, "Sample text")
        self.assertEqual(post.attachments[1].uri, "http://example.com/image.jpg")
        self.assertEqual(post.attachments[2].name, "Central Park")
        self.assertEqual(post.attachments[3].name, "Birthday Party")
        self.assertEqual(post.attachments[4].url, "http://example.com")

if __name__ == '__main__':
    unittest.main()