# -*- coding: utf-8 -*-

import json

# Abstract base class for entities
class AbstractEntity:
    """
    An abstract base class for entities, providing functionality for serialization to JSON.

    Methods:
        toJSON(): Serializes the object to a JSON string representation.
    """

    
    def __init__(self):
        """
        Initializes a new instance of AbstractEntity.
        
        This constructor is intended to be inherited by subclasses.
        """
        pass


    def toJSON(self):
        """
        Serializes the instance to a JSON string.

        Uses the instance's `__dict__` attribute to convert the object's properties
        to a dictionary, and then serializes it to a JSON string with indentation and
        sorted keys.

        Returns:
            str: The JSON string representation of the object.
        """
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4
        )