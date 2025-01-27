# -*- coding: utf-8 -*-

from .base import SocialMediaExportDeserializer
from ..entities import instagram as Instagram

class InstagramPostExportDeserializer(SocialMediaExportDeserializer):
    """
    A class responsible for deserializing Instagram post export data from a JSON structure.

    This class extends `SocialMediaExportDeserializer` and implements the deserialization logic
    for extracting and converting Instagram post data into corresponding Instagram entities like `Post`,
    `Media`, and `ExifData`.

    Methods:
        deserialize(data): Deserialize the provided JSON-like data into a list of `Post` objects.
    """

    def __init__(self):
        """
        Initializes an instance of the InstagramPostExportDeserializer class.
        """
        super().__init__()
    
    def deserialize(self, data):
        """
        Deserialize a JSONDecoder list into a list of Post objects.

        Args:
            data (list): A list of Instagram post export data, decoded from JSON.

        Returns:
            list: A list of `Post` objects populated with data extracted from the provided input.

        Notes:
            - The post's `title` and `timestamp` are handled differently based on the number of media items.
            - The method addresses a known issue with Unicode encoding, fixing mojibaking caused by Meta's exporter.
        """
        posts = []
        for item in data:
            # If the post has more than one media item,
            #  the title and timestamp are at the top level of the post.
            if len(item['media']) > 1:
                title = item['title']
                timestamp = item['creation_timestamp']
            
            # If the post has only one media item,
            #   the title and timestamp are part of the media item's data.
            else:
                title = item['media'][0]['title']
                timestamp = item['media'][0]['creation_timestamp']

            # Fix for the mojibaking bug in Meta's exporter.
            #  See: https://krvtz.net/posts/how-facebook-got-unicode-wrong.html
            title = title.encode('LATIN-1').decode('UTF-8')

            post = Instagram.Post(title, timestamp)
            
            # Add the entry's media objects to the post object.
            for media in item['media']:
                uri = media['uri']
                timestamp = media['creation_timestamp']
                
                # Create an empty ExifData object.
                exif_data = Instagram.ExifData()
                
                # Not all entries contain metadata.
                if 'media_metadata' in media:
                    
                    # If the media item is a video, its URI will contain the substring ".mp4" in it.
                    #  The metadata for videos and photos exists at different locations.
                    metadata_key = 'video_metadata' if '.mp4' in uri else 'photo_metadata'
                    
                    # Only attempt to set values that are in the data.
                    #   Not every post has every piece of possible metadata.
                    for attribute in media['media_metadata'][metadata_key]['exif_data'][0]:
                        if hasattr(exif_data, attribute):
                            setattr(exif_data, attribute, media['media_metadata'][metadata_key]['exif_data'][0][attribute])
                
                # Create a Media object and add the media to the Post object.
                media_item = Instagram.Media(uri, timestamp, exif_data)
                post.add_media(media_item)

            # Add the Post to the list of Posts.
            posts.append(post)

        return posts