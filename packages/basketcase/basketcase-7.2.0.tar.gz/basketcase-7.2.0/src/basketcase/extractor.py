import re
import typing
import logging
from datetime import datetime
from urllib.parse import urlparse

if typing.TYPE_CHECKING:
    import requests

from .models import Resource, ResourceImage, ResourceVideo, ExtractorError


class AbstractExtractor:
    """
    All extractors should extend this class.
    """
    api_headers = {'x-ig-app-id': '936619743392459'}

    def __init__(
            self,
            identifier: str,
            http_client: 'requests.Session',
            html_response: 'requests.Response',
    ):
        """
        :param identifier: resource ID for the API call (e.g. profile_id, media_id)
        :param http_client:
        :param html_response: the response from the first request (usually an HTML page)
        """
        self.id = identifier
        self.http_client = http_client
        self.html_response = html_response
        self.logger = logging.getLogger(__name__)

    def extract(self) -> set[Resource]:
        """
        Extractors must override this method with their implementation.
        :return:
        """
        pass

    def find_best_size(
        self,
        options: list,
        original_width: int = None,
        original_height: int = None
    ) -> dict:
        """
        Returns the best resolution from a list of "image_versions2.candidates" or "video_versions"
        :param original_height:
        :param original_width:
        :param options:
        :return:
        """
        selected = options[0]

        for option in options:
            if (original_height and original_width) and (
                option['width'] == original_width and option['height'] == original_height
            ):
                selected = option
                break

            if (option['width'] + option['height']) > (selected['width'] + selected['height']):
                selected = option

        return selected

    def extract_from_media_info_object(self, item: dict, user: dict | None = None) -> set[Resource]:
        """
        Traverses a common structure used by Instagram to return media info.
        :param item: Object containing media info
        :param user: Object containing user data, or at least `username`. Some extractors require this.
        :return:
        """
        downloadable = set()

        image_version = self.find_best_size(
            item['image_versions2']['candidates'],
            item['original_width'],
            item['original_height']
        )
        image_url = image_version['url']
        resource_id = item['id']

        if user:
            username = user['username']
        else:
            username = item['user']['username']

        downloadable.add(ResourceImage(
            url=image_url,
            id=resource_id,
            username=username
        ))

        if 'video_versions' in item:
            video_url = self.find_best_size(item['video_versions'])['url']

            downloadable.add(ResourceVideo(
                url=video_url,
                id=resource_id,
                username=username
            ))

        return downloadable


class PostExtractor(AbstractExtractor):
    def extract(self):
        downloadable = set()

        response = self.http_client.get(
            url=f'https://i.instagram.com/api/v1/media/{self.id}/info/',
            timeout=30,
            headers=AbstractExtractor.api_headers
        )

        response.raise_for_status()
        media_info = response.json()

        for item in media_info['items']:
            if 'carousel_media' in item:
                carousel_items = item['carousel_media']

                for carousel_item in carousel_items:
                    downloadable.update(self.extract_from_media_info_object(carousel_item, item['user']))
            else:
                downloadable.update(self.extract_from_media_info_object(item))

        return downloadable


class ProfileExtractor(AbstractExtractor):
    """
    Extractor for user profiles.
    """
    def _get_profile_picture(self) -> ResourceImage:
        url = urlparse(self.html_response.request.url)
        username = url.path.strip('/')
        self.logger.debug(f'Extracted username "{username}" from request URL')

        with self.http_client.get(
            url=f'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}',
            timeout=30,
            headers=AbstractExtractor.api_headers
        ) as response:
            response.raise_for_status()
            user_data = response.json()

            return ResourceImage(
                url=user_data['data']['user']['profile_pic_url_hd'],
                id=user_data['data']['user']['id'],
                username=username
            )

    def extract(self):
        downloadable = set()

        response = self.http_client.get(
            url=f'https://www.instagram.com/api/v1/feed/reels_media/?reel_ids={self.id}',
            timeout=30,
            headers=AbstractExtractor.api_headers
        )

        response.raise_for_status()
        media_info = response.json()

        for reel_id, reel_item in media_info['reels'].items():
            seen = datetime.fromtimestamp(reel_item['seen'])

            for item in reel_item['items']:
                downloadable.update(self.extract_from_media_info_object(item, reel_item['user']))

                taken_at = datetime.fromtimestamp(item['taken_at'])
                if seen >= taken_at: self.logger.debug(f'Story created at {taken_at} marked as seen ({seen})')

        downloadable.add(self._get_profile_picture())

        return downloadable


class HighlightExtractor(AbstractExtractor):
    def extract(self):
        downloadable = set()

        response = self.http_client.get(
            url=f'https://www.instagram.com/api/v1/feed/reels_media/?reel_ids=highlight:{self.id}',
            timeout=30,
            headers=AbstractExtractor.api_headers
        )

        response.raise_for_status()
        media_info = response.json()

        for reel_id, reel_item in media_info['reels'].items():
            for item in reel_item['items']:
                user = reel_item['user']

                downloadable.update(self.extract_from_media_info_object(item, user))

        return downloadable


class Extractor:
    """
    This is where most of the scraping work is done.
    """

    def __init__(
            self,
            http_client: 'requests.Session'
    ):
        self.http_client = http_client

    def _get_extractor(self, url: str) -> AbstractExtractor:
        """
        :raises ExtractorError: if no extractor was found for url
        """
        response = self.http_client.get(url, timeout=30, allow_redirects=False)
        response.raise_for_status()

        media_id = re.search(r'"media_id"\s*:\s*"(.*?)"', response.text)
        profile_id = re.search(r'"profile_id"\s*:\s*"(.*?)"', response.text)
        highlight_id = re.search(r'"highlight_id":\s?"highlight:(.*?)"', response.text)

        if profile_id:
            return ProfileExtractor(
                identifier=profile_id.group(1),
                http_client=self.http_client,
                html_response=response
            )

        if media_id:
            return PostExtractor(
                identifier=media_id.group(1),
                http_client=self.http_client,
                html_response=response
            )

        if highlight_id:
            return HighlightExtractor(
                identifier=highlight_id.group(1),
                http_client=self.http_client,
                html_response=response
            )

        raise ExtractorError(f'Failed to locate a suitable extractor for url: {url}')

    def extract_from_url(self, url: str) -> set[Resource]:
        """
        Extract downloadable media from a resource URL.
        :param url: One of the supported URLs
        :return: `set` of Resource objects
        """
        downloadable = set()
        extractor = self._get_extractor(url)
        downloadable.update(extractor.extract())

        return downloadable
