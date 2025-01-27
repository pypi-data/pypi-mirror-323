import unittest
from landowner.deserializers.instagram import InstagramPostExportDeserializer
from landowner.entities import instagram as Instagram

class TestInstagramPostExportDeserializer(unittest.TestCase):

    def setUp(self):
        self.deserializer = InstagramPostExportDeserializer()

    def test_deserialize_single_media_post(self):
        data = [{
            'media': [{
                'title': 'Single media post',
                'creation_timestamp': 1609459200,
                'uri': 'http://example.com/media1.jpg'
            }]
        }]
        posts = self.deserializer.deserialize(data)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].title, 'Single media post')
        self.assertEqual(posts[0].timestamp, 1609459200)
        self.assertEqual(len(posts[0].media), 1)
        self.assertEqual(posts[0].media[0].uri, 'http://example.com/media1.jpg')

    def test_deserialize_multiple_media_post(self):
        data = [{
            'title': 'Multiple media post',
            'creation_timestamp': 1609459200,
            'media': [
                {'uri': 'http://example.com/media1.jpg', 'creation_timestamp': 1609459200},
                {'uri': 'http://example.com/media2.jpg', 'creation_timestamp': 1609459201}
            ]
        }]
        posts = self.deserializer.deserialize(data)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].title, 'Multiple media post')
        self.assertEqual(posts[0].timestamp, 1609459200)
        self.assertEqual(len(posts[0].media), 2)
        self.assertEqual(posts[0].media[0].uri, 'http://example.com/media1.jpg')
        self.assertEqual(posts[0].media[1].uri, 'http://example.com/media2.jpg')

    def test_deserialize_with_exif_data(self):
        data = [{
            'media': [{
                'title': 'Post with exif data',
                'creation_timestamp': 1609459200,
                'uri': 'http://example.com/media1.jpg',
                'media_metadata': {
                    'photo_metadata': {
                        'exif_data': [{
                            'iso': 400,
                            'device_id': 'EOS 80D'
                        }]
                    }
                }
            }]
        }]
        posts = self.deserializer.deserialize(data)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].title, 'Post with exif data')
        self.assertEqual(posts[0].timestamp, 1609459200)
        self.assertEqual(len(posts[0].media), 1)
        self.assertEqual(posts[0].media[0].uri, 'http://example.com/media1.jpg')
        self.assertEqual(posts[0].media[0].exif_data.iso, 400)
        self.assertEqual(posts[0].media[0].exif_data.device_id, 'EOS 80D')

    def test_with_real_archival_data(self):
        data = [{
            "media": [{
                "uri": "media/posts/205907/63213211_2606321729399040_8169302857697949875_n_18089344625066103.jpg",
                "media_path_INTERNAL": "",
                "type_INTERNAL": "",
                "creation_timestamp": 1563825037,
                "media_metadata": {
                    "photo_metadata": {
                        "exif_data": [
                            {
                                "iso": 100,
                                "focal_length": "3.99",
                                "lens_model": "iPhone 8 Plus back dual camera 3.99mm f/1.8",
                                "scene_capture_type": "standard",
                                "software": "12.3.2",
                                "device_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
                                "scene_type": 1,
                                "camera_position": "back",
                                "lens_make": "Apple",
                                "date_time_digitized": "2019:07:22 12:21:42",
                                "date_time_original": "2019:07:22 12:21:42",
                                "source_type": "library",
                                "aperture": "1.6959938128383605",
                                "shutter_speed": "3.2065219045300304",
                                "metering_mode": "5"
                            }
                        ]
                    }
                },
                "title": "BLT; hold the lettuce, hold the bacon. \u00f0\u009f\u008d\u0085"
            }
            ]
        }
        ]
        posts = self.deserializer.deserialize(data)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].title, 'BLT; hold the lettuce, hold the bacon. 🍅')
        self.assertEqual(posts[0].timestamp, 1563825037)
        self.assertEqual(len(posts[0].media), 1)
        self.assertEqual(posts[0].media[0].uri, 'media/posts/205907/63213211_2606321729399040_8169302857697949875_n_18089344625066103.jpg')
        self.assertEqual(posts[0].media[0].exif_data.iso, 100)
        self.assertEqual(posts[0].media[0].exif_data.device_id, 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX')

if __name__ == '__main__':
    unittest.main()