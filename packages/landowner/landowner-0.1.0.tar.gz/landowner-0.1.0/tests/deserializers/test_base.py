import os
import unittest
import json
from landowner.entities.base import AbstractEntity
from landowner.deserializers.base import SocialMediaExportDeserializer

# -*- coding: utf-8 -*-


class TestBaseDeserializer(unittest.TestCase):
    """Test cases for SocialMediaExportDeserializer."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.deserializer = SocialMediaExportDeserializer()

    def test_initialization(self):
        """Test the initialization of AbstractEntity."""
        self.assertIsInstance(self.deserializer, SocialMediaExportDeserializer)

    def test_load_json_file(self):
        """Test loading a well-formed JSON file."""
        test_json = '{"key": "value"}'
        with open('test.json', 'w') as f:
            f.write(test_json)
        
        result = self.deserializer.load_json_file('test.json')
        self.assertEqual(result, {"key": "value"})

    def test_load_json_file_invalid_path(self):
        """Test loading a JSON file with an invalid path."""
        with self.assertRaises(FileNotFoundError):
            self.deserializer.load_json_file('invalid_path.json')

    def test_load_json_file_malformed_json(self):
        """Test loading a malformed JSON file."""
        malformed_json = '{"key": "value"'
        with open('malformed.json', 'w') as f:
            f.write(malformed_json)
        
        with self.assertRaises(json.JSONDecodeError):
            self.deserializer.load_json_file('malformed.json')

    def test_deserialize_not_implemented(self):
        """Test that deserialize method raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            self.deserializer.deserialize()

    def tearDown(self):
        if os.path.exists('test.json'):
            os.remove('test.json')
        if os.path.exists('malformed.json'):
            os.remove('malformed.json')
    
if __name__ == '__main__':
    unittest.main()