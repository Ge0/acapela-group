"""Base classes for Acapela Group website communication."""
import requests


try:
    from urllib.parse import urlparse  # Python3 standard module.
except ImportError:
    from urlparse import urlparse


class AcapelaGroupError(Exception):
    """Base exception class for Acapela Group related errors."""


class InvalidCredentialsError(AcapelaGroupError):
    """Exception class for invalid credentials error."""


class NeedsUpdateError(AcapelaGroupError):
    """Exception class thrown when the code cannot scrap the website.

    Basically, it means that the module needs some update to keep interfacing
    with the Acapela Group website.
    """


class AcapelaGroup:
    """Client class for Acapela Group website interaction."""

    def __init__(self, base_url="http://www.acapela-group.com"):
        """Create an AcapelaGroup session handler."""
        self._base_url = base_url
        self._http_session = requests.Session()

    @property
    def base_url(self):
        """str: Get the base url of the instance.

        Being able to set the base url can be useful for testing purposes. The
        base url cannot be changed once the instance has been created.
        """
        return self._base_url

    def build_url(self, path=''):
        """Build a full URL with `self.base_url` and `path`.

        The result is simply `self.base_url`/`path`.

        Args:
            path (str): The path to build the URL with. Defaults to ''.

        Example:
            if the base url is 'http://www.acapela-group.com' and that the
            path is 'wp-login.php', then the method will return
            'http://www.acapela-group.com/wp-login.php'.

        Returns:
            str: Build url.
        """
        return '{}/{}'.format(self._base_url, path)

    def authenticate(self, username: str, password: str):
        """Authenticate against the website using `login` and `password`.

        The session will use the provided credentials to scrap the website.
        It is useful mostly for retrieving sound with no background music
        set when an anonymous user listens to a text-to-speech sound.

        To obtain some credentials, you must register here:
        http://www.acapela-group.com/register/

        Args:
            username: The account's username used for registration.
            password: The account's password used for registration.

        Note:
            Be careful: Acapela Group does not use HTTPS, so your credentials
                are passing through networks as plain text. If no exception
                is raised, then the authentication succeeded.

        Raises:
            InvalidCredentialsError: if the authentication fails because of a
                bad `login`/`password` combination.
        """

        data = {
            'log': username,
            'pwd': password,
            'wp-submit': '',
            'redirect_to': self.build_url()  # Redirect to the index.
        }

        response = self._http_session.post(self.build_url('wp-login.php'),
                                           allow_redirects=False,
                                           data=data)
        try:
            location = response.headers["Location"]
        except KeyError as exn:
            raise NeedsUpdateError(
                "Could not get Location header from login.") from exn
        else:
            parse_result = urlparse(location)

            if parse_result.path == '/login/' and \
                    parse_result.query == 'the_error=incorrect_password':
                raise InvalidCredentialsError("Could not authenticate.")
