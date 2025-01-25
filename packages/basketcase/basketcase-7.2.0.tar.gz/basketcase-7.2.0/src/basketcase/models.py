from dataclasses import dataclass, field


@dataclass
class Session:
    """
    A session cookie.
    """
    rowid: int | None
    description: str
    cookie_id: str
    is_default: int
    first_used: str | None = field(default=None)


@dataclass(frozen=True)
class Resource:
    """
    A remote resource (e.g. image or video), its URL and other metadata.
    """
    url: str
    id: str
    username: str
    extension: str = field(default=None, init=False)

    def get_extension(self) -> str:
        """
        Returns the file extension.
        :return:
        """
        # This is equivalent to calling ResourceImage.extension or ResourceVideo.extension
        # without knowing which one.
        return type(self).extension


class ResourceImage(Resource):
    extension = '.jpg'


class ResourceVideo(Resource):
    extension = '.mp4'


class BasketCaseError(Exception):
    """
    Base exception for all BasketCase errors.
    """


class ExtractorError(BasketCaseError):
    pass
