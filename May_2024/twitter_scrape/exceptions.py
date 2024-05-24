class TwitterException(Exception):
    """Generic exception that all other TikTok errors are children of."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CaptchaException(TwitterException):
    """TikTok is showing captcha"""


class NotFoundException(TwitterException):
    """TikTok indicated that this object does not exist."""


class EmptyResponseException(TwitterException):
    """TikTok sent back an empty response."""


class SoundRemovedException(TwitterException):
    """This TikTok sound has no id from being removed by TikTok."""


class InvalidJSONException(TwitterException):
    """TikTok returned invalid JSON."""


class NotAvailableException(TwitterException):
    """The requested object is not available in this region."""

class TimeoutException(TwitterException):
    """Timed out trying to get content from TikTok"""

class ApiFailedException(TwitterException):
    """TikTok API is failing"""
