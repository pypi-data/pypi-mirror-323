# -*- coding: utf-8 -*-
# Objects representing exported data
import json
from landowner.entities.base import AbstractEntity

class Post(AbstractEntity):
    """
    Represents a blog or forum post with a title, timestamp, content, tags, and attachments.

    Attributes:
        title (str): The title of the post. Defaults to an empty string.
        timestamp (str): The timestamp indicating when the post was created or last updated. Defaults to an empty string.
        data (PostData): The content and update details of the post.
        tags (list): A list of tags (Tag objects or strings) associated with the post. Defaults to an empty list.
        attachments (list): A list of attachments (e.g., file paths or objects) associated with the post. Defaults to an empty list.
    """

    def __init__(self, title="", timestamp=""):
        """
        Initializes a new instance of Post.

        Args:
            title (str): The title of the post. Defaults to an empty string.
            timestamp (str): The timestamp for when the post was created or updated. Defaults to an empty string.
        """
        self.title = title
        self.timestamp = timestamp
        self.data = PostData()
        self.tags = []
        self.attachments = []


class Tag(AbstractEntity):
    """
    Represents a tag with a name.

    Attributes:
        name (str): The name of the tag. Defaults to an empty string.
    """

    def __init__(self, name=""):
        """
        Initializes a new instance of Tag.

        Args:
            name (str): The name of the tag. Defaults to an empty string.
        """
        self.name = name

    def __str__(self) -> str:
        """
        Returns the string representation of the tag.

        Returns:
            str: The name of the tag.
        """
        return self.name


class PostData(AbstractEntity):
    """
    Represents a post with text content and a timestamp for updates.

    Attributes:
        text (str): The text content of the post. Defaults to an empty string.
        update_timestamp (str): A timestamp indicating the last update time of the post. Defaults to an empty string.
    """

    def __init__(self, text="", update_timestamp=""):
        """
        Initializes a new instance of PostData.

        Args:
            text (str): The text content of the post. Defaults to an empty string.
            update_timestamp (str): The last update timestamp of the post. Defaults to an empty string.
        """
        self.text = text
        self.update_timestamp = update_timestamp

    def __repr__(self) -> str:
        """
        Returns a JSON representation of the PostData object.

        Returns:
            str: A JSON string representing the object's attributes.
        """
        return self.toJSON()


class TextAttachment(AbstractEntity):
    """
    Represents a text-based attachment for a post.

    Attributes:
        text (str): The content of the text attachment. Defaults to an empty string.
    """

    def __init__(self, text=""):
        """
        Initializes a new instance of TextAttachment.

        Args:
            text (str): The content of the text attachment. Defaults to an empty string.
        """
        self.text = text


class Media(AbstractEntity):
    """
    Represents a media object, typically a photo or video.

    Attributes:
        uri (str): The URI or file path to the media. Defaults to an empty string.
        title (str): The title of the media. Defaults to an empty string.
        description (str): A brief description of the media. Defaults to an empty string.
        timestamp (str): The timestamp indicating when the media was created or captured. Defaults to an empty string.
        exif_data (str): Metadata associated with the media (e.g., camera settings). Defaults to an empty string.
    """

    def __init__(self="", uri="", title="", description="", timestamp="", exif_data=""):
        """
        Initializes a new instance of Media.

        Args:
            uri (str): The URI or file path to the media. Defaults to an empty string.
            title (str): The title of the media. Defaults to an empty string.
            description (str): A brief description of the media. Defaults to an empty string.
            timestamp (str): The timestamp indicating when the media was created or captured. Defaults to an empty string.
            exif_data (str): Metadata associated with the media (e.g., camera settings). Defaults to an empty string.
        """
        self.uri = uri
        self.title = title
        self.description = description
        self.timestamp = timestamp
        self.exif_data = exif_data


class Place(AbstractEntity):
    """
    Represents a physical location with geographic coordinates, a name, and additional details.

    Attributes:
        latitude (str): The latitude of the location. Defaults to an empty string.
        longitude (str): The longitude of the location. Defaults to an empty string.
        name (str): The name of the location. Defaults to an empty string.
        address (str): The address of the location. Defaults to an empty string.
        url (str): A URL providing more information about the location. Defaults to an empty string.
    """

    def __init__(self, latitude="", longitude="", name="", address="", url=""):
        """
        Initializes a new instance of Place.

        Args:
            latitude (str): The latitude of the location. Defaults to an empty string.
            longitude (str): The longitude of the location. Defaults to an empty string.
            name (str): The name of the location. Defaults to an empty string.
            address (str): The address of the location. Defaults to an empty string.
            url (str): A URL providing more information about the location. Defaults to an empty string.
        """
        self.latitude = latitude
        self.longitude = longitude
        self.name = name
        self.address = address
        self.url = url


class Event(AbstractEntity):
    """
    Represents an event with a name, timing, description, and location.

    Attributes:
        name (str): The name of the event. Defaults to an empty string.
        start_timestamp (str): The starting timestamp of the event. Defaults to an empty string.
        end_timestamp (str): The ending timestamp of the event. Defaults to an empty string.
        description (str): A brief description of the event. Defaults to an empty string.
        create_timestamp (str): The timestamp when the event was created. Defaults to an empty string.
        place (str): The location of the event, represented as a string or Place object. Defaults to an empty string.
    """

    def __init__(
            self,
            name="",
            start_timestamp="",
            end_timestamp="",
            description="",
            create_timestamp="",
            place=""
            ):
        """
        Initializes a new instance of Event.

        Args:
            name (str): The name of the event. Defaults to an empty string.
            start_timestamp (str): The starting timestamp of the event. Defaults to an empty string.
            end_timestamp (str): The ending timestamp of the event. Defaults to an empty string.
            description (str): A brief description of the event. Defaults to an empty string.
            create_timestamp (str): The timestamp when the event was created. Defaults to an empty string.
            place (str): The location of the event, represented as a string or Place object. Defaults to an empty string.
        """
        self.name = name
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.description = description
        self.create_timestamp = create_timestamp
        self.place = place


class ExternalContext(AbstractEntity):
    """
    Represents external contextual information, such as references, sources, or links.

    Attributes:
        name (str): The name or title of the external context. Defaults to an empty string.
        source (str): The source or origin of the external context. Defaults to an empty string.
        url (str): The URL associated with the external context. Defaults to an empty string.
    """

    def __init__(self, name="", source="", url=""):
        """
        Initializes a new instance of ExternalContext.

        Args:
            name (str): The name or title of the external context. Defaults to an empty string.
            source (str): The source or origin of the external context. Defaults to an empty string.
            url (str): The URL associated with the external context. Defaults to an empty string.
        """
        self.name = name
        self.source = source
        self.url = url


class ExifData(AbstractEntity):
    """
    Represents Exif metadata for media objects, capturing details about how and when the media was created.

    Attributes:
        latitude (str): The latitude where the media was captured. Defaults to an empty string.
        longitude (str): The longitude where the media was captured. Defaults to an empty string.
        iso (str): The ISO sensitivity setting used for the media. Defaults to an empty string.
        focal_length (str): The focal length of the lens in use. Defaults to an empty string.
        lens_model (str): The model of the lens used to capture the media. Defaults to an empty string.
        scene_capture_type (str): The scene capture type (e.g., standard, landscape, portrait). Defaults to an empty string.
        software (str): The software used to process or edit the media. Defaults to an empty string.
        device_id (str): The unique identifier of the capturing device. Defaults to an empty string.
        scene_type (str): The type of scene captured (e.g., directly photographed). Defaults to an empty string.
        camera_position (str): The position of the camera when capturing the media. Defaults to an empty string.
        lens_make (str): The manufacturer of the lens used. Defaults to an empty string.
        date_time_digitized (str): The timestamp when the media was digitized. Defaults to an empty string.
        date_time_original (str): The original timestamp when the media was created. Defaults to an empty string.
        source_type (str): The type of source used to create the media. Defaults to an empty string.
        aperture (str): The aperture value used during capture. Defaults to an empty string.
        shutter_speed (str): The shutter speed value. Defaults to an empty string.
        metering_mode (str): The metering mode used during capture. Defaults to an empty string.
        upload_ip (str): The IP address from which the media was uploaded. Defaults to an empty string.
        taken_timestamp (str): The timestamp when the media was taken. Defaults to an empty string.
        orientation (str): The orientation of the media (e.g., landscape, portrait). Defaults to an empty string.
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
            upload_ip="",
            taken_timestamp="",
            orientation="",
    ):
        """
        Initializes a new instance of ExifData.

        Args:
            latitude (str): The latitude where the media was captured. Defaults to an empty string.
            longitude (str): The longitude where the media was captured. Defaults to an empty string.
            iso (str): The ISO sensitivity setting used for the media. Defaults to an empty string.
            focal_length (str): The focal length of the lens in use. Defaults to an empty string.
            lens_model (str): The model of the lens used to capture the media. Defaults to an empty string.
            scene_capture_type (str): The scene capture type (e.g., standard, landscape, portrait). Defaults to an empty string.
            software (str): The software used to process or edit the media. Defaults to an empty string.
            device_id (str): The unique identifier of the capturing device. Defaults to an empty string.
            scene_type (str): The type of scene captured (e.g., directly photographed). Defaults to an empty string.
            camera_position (str): The position of the camera when capturing the media. Defaults to an empty string.
            lens_make (str): The manufacturer of the lens used. Defaults to an empty string.
            date_time_digitized (str): The timestamp when the media was digitized. Defaults to an empty string.
            date_time_original (str): The original timestamp when the media was created. Defaults to an empty string.
            source_type (str): The type of source used to create the media. Defaults to an empty string.
            aperture (str): The aperture value used during capture. Defaults to an empty string.
            shutter_speed (str): The shutter speed value. Defaults to an empty string.
            metering_mode (str): The metering mode used during capture. Defaults to an empty string.
            upload_ip (str): The IP address from which the media was uploaded. Defaults to an empty string.
            taken_timestamp (str): The timestamp when the media was taken. Defaults to an empty string.
            orientation (str): The orientation of the media (e.g., landscape, portrait). Defaults to an empty string.
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
        self.upload_ip = upload_ip
        self.taken_timestamp = taken_timestamp
        self.orientation = orientation