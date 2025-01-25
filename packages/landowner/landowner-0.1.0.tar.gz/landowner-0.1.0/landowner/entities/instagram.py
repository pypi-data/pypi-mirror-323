# -*- coding: utf-8 -*-

from landowner.entities.base import AbstractEntity

class Post(AbstractEntity):
    """
    Represents a single post, typically an entry from exported data, with a title, timestamp, and associated media.

    Attributes:
        title (str): The title of the post. Defaults to an empty string.
        timestamp (str): The timestamp when the post was created or published. Defaults to an empty string.
        media (list): A list of media objects associated with the post. Defaults to an empty list.

    Methods:
        add_media(media): Adds a media object to the post's media list.
    """


    def __init__(self, title="", timestamp=""):
        """
        Initializes a new instance of the Post class.

        Args:
            title (str): The title of the post. Defaults to an empty string.
            timestamp (str): The timestamp when the post was created or published. Defaults to an empty string.
        """
        self.title = title
        self.timestamp = timestamp
        self.media = []

    def add_media(self, media):
        """
        Adds a media object to the post's media list.

        Args:
            media: A media object (e.g., image, video) to associate with the post.
        """
        self.media.append(media)


class Media(AbstractEntity):
    """
    Represents a media object, typically a photo or video, with associated metadata.

    Attributes:
        uri (str): The URI or path to the media file. Defaults to an empty string.
        timestamp (str): The timestamp when the media was created or uploaded. Defaults to an empty string.
        exif_data (str): Exif metadata associated with the media, such as camera settings and geolocation. Defaults to an empty string.
    
    Methods:
        None
    """

    def __init__(self, uri="", timestamp="", exif_data=""):
        """
        Initializes a new instance of the Media class.

        Args:
            uri (str): The URI or path to the media file. Defaults to an empty string.
            timestamp (str): The timestamp when the media was created or uploaded. Defaults to an empty string.
            exif_data (str): Exif metadata associated with the media. Defaults to an empty string.
        """
        self.uri = uri
        self.timestamp = timestamp
        self.exif_data = exif_data


class ExifData(AbstractEntity):
    """
    Represents Exif metadata for media objects, capturing relevant information about how and when the media was created.

    This includes camera settings, device information, and scene-related data that may be helpful for analyzing or processing 
    media files like photos and videos.

    Attributes:
        latitude (str): The latitude where the media was captured. Defaults to an empty string.
        longitude (str): The longitude where the media was captured. Defaults to an empty string.
        iso (str): The ISO sensitivity setting used for the media. Defaults to an empty string.
        focal_length (str): The focal length of the lens in use during capture. Defaults to an empty string.
        lens_model (str): The model of the lens used during capture. Defaults to an empty string.
        scene_capture_type (str): The type of scene captured, such as landscape, portrait, or standard. Defaults to an empty string.
        software (str): The software used to process or edit the media. Defaults to an empty string.
        device_id (str): The unique identifier of the device used to capture the media. Defaults to an empty string.
        scene_type (str): The type of scene captured, such as direct or scene with special settings. Defaults to an empty string.
        camera_position (str): The camera's position or orientation during capture. Defaults to an empty string.
        lens_make (str): The manufacturer of the lens used during capture. Defaults to an empty string.
        date_time_digitized (str): The timestamp when the media was digitized. Defaults to an empty string.
        date_time_original (str): The original timestamp when the media was taken. Defaults to an empty string.
        source_type (str): The source type of the media, such as camera or scanner. Defaults to an empty string.
        aperture (str): The aperture setting used during capture. Defaults to an empty string.
        shutter_speed (str): The shutter speed value used during capture. Defaults to an empty string.
        metering_mode (str): The metering mode used during capture, such as matrix or center-weighted. Defaults to an empty string.

    Methods:
        None
    """

    def __init__(
            self,
            latitude="",
            longitude="",
            iso="",
            focal_length="",
            lens_model="",
            scene_capture_type="",
            software="",
            device_id="",
            scene_type="",
            camera_position="",
            lens_make="",
            date_time_digitized="",
            date_time_original="",
            source_type="",
            aperture="",
            shutter_speed="",
            metering_mode="",
    ):
        """
        Initializes a new instance of the ExifData class.

        Args:
            latitude (str): The latitude where the media was captured. Defaults to an empty string.
            longitude (str): The longitude where the media was captured. Defaults to an empty string.
            iso (str): The ISO sensitivity setting used for the media. Defaults to an empty string.
            focal_length (str): The focal length of the lens in use during capture. Defaults to an empty string.
            lens_model (str): The model of the lens used during capture. Defaults to an empty string.
            scene_capture_type (str): The type of scene captured, such as landscape, portrait, or standard. Defaults to an empty string.
            software (str): The software used to process or edit the media. Defaults to an empty string.
            device_id (str): The unique identifier of the device used to capture the media. Defaults to an empty string.
            scene_type (str): The type of scene captured, such as direct or scene with special settings. Defaults to an empty string.
            camera_position (str): The camera's position or orientation during capture. Defaults to an empty string.
            lens_make (str): The manufacturer of the lens used during capture. Defaults to an empty string.
            date_time_digitized (str): The timestamp when the media was digitized. Defaults to an empty string.
            date_time_original (str): The original timestamp when the media was taken. Defaults to an empty string.
            source_type (str): The source type of the media, such as camera or scanner. Defaults to an empty string.
            aperture (str): The aperture setting used during capture. Defaults to an empty string.
            shutter_speed (str): The shutter speed value used during capture. Defaults to an empty string.
            metering_mode (str): The metering mode used during capture, such as matrix or center-weighted. Defaults to an empty string.
        """
        self.latitude = latitude
        self.longitude = longitude
        self.iso = iso
        self.focal_length = focal_length
        self.lens_model = lens_model
        self.scene_capture_type = scene_capture_type
        self.software = software
        self.device_id = device_id
        self.scene_type = scene_type
        self.camera_position = camera_position
        self.lens_make = lens_make
        self.date_time_digitized = date_time_digitized
        self.date_time_original = date_time_original
        self.source_type = source_type
        self.aperture = aperture
        self.shutter_speed = shutter_speed
        self.metering_mode = metering_mode