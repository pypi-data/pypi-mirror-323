import stat
from pathlib import Path
import logging
import requests

from . import extractor
from . import authenticator
from . import storage

from .models import Resource


class BasketCase:
    """
    BasketCase, download images and videos from Instagram.

    This is the main class, where filesystem operations are done.
    Other components are instantiated and called here.
    """
    def __init__(
        self,
        loglevel: str | None
    ):
        # Setup logger
        if loglevel is None:
            loglevel = 'warning'
        numeric_level = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f'Invalid log level: {loglevel}')
        logging.basicConfig(level=numeric_level)
        self.logger = logging.getLogger(__name__)

        # Create application data directory
        self.data_dir = f'{Path.home()!s}/.basketcase'
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.data_dir).chmod(stat.S_IRWXU)

        # Set default output directory
        self.output_dir = f'{Path.cwd()!s}'

        # Initialize dependencies
        self.http_client = requests.Session()
        self.storage = storage.Storage(self.data_dir)
        self.authenticator = authenticator.Authenticator(self.http_client, self.storage)
        self.extractor = extractor.Extractor(http_client=self.http_client)

    def get(self, url: str):
        """
        Downloads resources from the URL.
        This is just a shortcut.
        :param url: One of the supported URL types
        :return:
        """
        self.logger.warning(f'get() is deprecated. Use get_resources_from_url() and download() instead.')
        resources = self.get_resources_from_url(url)

        for resource in resources:
            self.download(resource)

    def get_resources_from_url(self, url: str) -> set[Resource]:
        """
        Returns the set of resources extracted from the URL.
        :param url: One of the supported URL types
        :return:
        """
        return self.extractor.extract_from_url(url)

    def download(self, resource: Resource):
        """
        Downloads a resource and writes it to the output directory.
        :param resource:
        :return:
        """
        user_dir = f'{self.output_dir}/{resource.username}'
        Path(user_dir).mkdir(parents=True, exist_ok=True)

        with self.http_client.get(resource.url, timeout=30) as response:
            response.raise_for_status()

            with open(f'{user_dir}/{resource.id}{resource.get_extension()}', mode='w+b') as file:
                file.write(response.content)
