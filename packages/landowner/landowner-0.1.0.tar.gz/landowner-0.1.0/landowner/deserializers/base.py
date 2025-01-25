# -*- coding: utf-8 -*-

import json

class SocialMediaExportDeserializer:
    """
    A class responsible for deserializing social media export data from a JSON file.
    
    This class provides methods to load JSON data from a file and deserialize it. Subclasses should
    implement the `deserialize` method to handle the specific deserialization logic for different formats.

    Methods:
        load_json_file(file): Reads a well-formed JSON file and returns its data as a Python object.
        deserialize(): An abstract method meant to be overridden by subclasses to handle custom deserialization logic.
    """

    def __init__(self):
        """
        Initializes a new instance of the SocialMediaExportDeserializer class.
        """
        pass

    def load_json_file(self, file):
        """
        Reads a well-formed JSON file and returns a list containing its data.

        This method opens the provided file, reads its contents, and loads the data using the JSON
        module, returning a list of Python objects parsed from the JSON structure.

        Args:
            file (str): The path to the local JSON file to be read.

        Returns:
            list: A list containing nested dictionaries, lists, and other values as parsed from the JSON data.

        Raises:
            FileNotFoundError: If the provided file path does not exist.
            JSONDecodeError: If the file content is not valid JSON.
            IOError: For any issues encountered while reading the file.
        """

        # TODO: Handle exceptions for file access, file format, and malformed JSON data.
        with open(file) as f:
            data = json.loads(f.read())
        return data
    
    def deserialize(self):
        """
        Abstract method to be implemented by subclasses.

        This method should be overridden by subclasses to implement custom deserialization logic
        for a specific social media export format.

        Raises:
            NotImplementedError: If this method is not overridden by a subclass.
        """
        
        raise NotImplementedError('This method is meant to be overwritten by subclasses.')