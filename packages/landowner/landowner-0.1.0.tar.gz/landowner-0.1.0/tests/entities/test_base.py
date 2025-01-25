import unittest
import json
from landowner.entities.base import AbstractEntity

# -*- coding: utf-8 -*-


class TestAbstractEntity(unittest.TestCase):
    """Test cases for AbstractEntity."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.entity = AbstractEntity()

    def test_toJSON(self):
        """Test the toJSON method."""
        expected_json = json.dumps(
            self.entity,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4
        )
        self.assertEqual(self.entity.toJSON(), expected_json)

    def test_initialization(self):
        """Test the initialization of AbstractEntity."""
        self.assertIsInstance(self.entity, AbstractEntity)

if __name__ == '__main__':
    unittest.main()