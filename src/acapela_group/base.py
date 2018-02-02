"""Base classes for Acapela Group website communication."""
import aiohttp
import re
from urllib.parse import urlparse

import requests

from .language import LANGUAGES

_MP3_REGEX = re.compile(r"var myPhpVar = '(.+?)';")


class AcapelaGroupError(Exception):
    """Base exception class for Acapela Group related errors."""


class TooManyInvalidLoginAttemptsError(AcapelaGroupError):
    """Exception class thrown when locked out for too many login attempts."""


class InvalidCredentialsError(AcapelaGroupError):
    """Exception class for invalid credentials error."""


class NeedsUpdateError(AcapelaGroupError):
    """Exception class thrown when the code cannot scrap the website.

    Basically, it means that the module needs some update to keep interfacing
    with the Acapela Group website.
    """


class LanguageNotSupportedError(AcapelaGroupError):
    """Exception class thrown when the language is not supported.

    For a complete list of supported languages, see language.py.
    """


class AcapelaGroupAsync:
    """Asynchronous client class for Acapela Group website interaction."""

    def __init__(self, base_url="http://www.acapela-group.com"):
        """Create an asynchronous AcapelaGroup session handler."""
        self._base_url = base_url
        self._http_session = None

    async def __aenter__(self):
        """Instantiate an http session with AcapelaGroup."""
        self._http_session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Uninstantiate the http session with AcapelaGroup."""
        self._http_session.close()

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

    async def authenticate(self, username: str, password: str):
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
            AcapelaGroupError: something went wrong while authenticating.

        """
        data = {
            'log': username,
            'pwd': password,
            'wp-submit': '',
            'redirect_to': self.build_url()  # Redirect to the index.
        }

        response = await self._http_session.post(
            self.build_url('wp-login.php'),
            allow_redirects=False,
            data=data)

        text = await response.text()

        if text == \
                ("You have been locked out due to "
                 "too many invalid login attempts."):
            raise TooManyInvalidLoginAttemptsError(
                "Looks like you are screwed because of too many login "
                "attempts. Try with another IP maybe.")

        try:
            location = response.headers["Location"]
        except KeyError as exn:
            raise NeedsUpdateError(
                "Could not get Location header from login. "
                "The module might need an update.") from exn
        else:
            parse_result = urlparse(location)
            if parse_result.path == '/login/' and \
                    parse_result.query == 'the_error=incorrect_password':
                raise InvalidCredentialsError(
                    "Wrong couple of login/password.")

            # Go to the index to simulate the Location.
            await self._http_session.get(location)

    async def get_mp3_url(self, language, voice, text):
        """Retrieve the mp3 url associated to the settings.

        To see the list of supported languages, check the `language` module.

        Args:
            language (str): The language to use for the acapela.
            voice (str): The voice name to use for the acapela.
            text (str): the text to translate to speech.

        Raises:
            NeedsUpdateError: The module needs an update since the mp3
                url could not have been extracted, somehow.

        Returns:
            str: An HTTP url pointing to the generated mp3.

        """
        try:
            language_code = LANGUAGES[language.upper()]
        except KeyError:
            raise LanguageNotSupportedError(
                "The language {} is not supported.".format(language))

        target = self.build_url(
            "demo-tts/DemoHTML5Form_V2.php?langdemo=Powered+by+"
            "<a+href=\"http://www.acapela-vaas.com\">Acapela+Vo"
            "ice+as+a+Service</a>.+For+demo+and+evaluation+purp"
            "ose+only,+for+commercial+use+of+generated+sound+fi"
            "les+please+go+to+<a+href=\"http://www.acapela-box."
            "com\">www.acapela-box.com</a>")

        # What is that for?!
        data = {
            '0': 'Leila',
            '1': 'Laia',
            '2': 'Eliska',
            '3': 'Mette',
            '4': 'Zoe',
            '5': 'Jasmijn',
            '6': 'Tyler',
            '7': 'Deepa',
            '8': 'Rhona',
            '9': 'Rachel',
            '10': 'Sharon',
            '11': 'Hanna',
            '12': 'Sanna',
            '13': 'Manon-be',
            '14': 'Louise',
            '16': 'Claudia',
            '17': 'Dimitris',
            '18': 'Fabiana',
            '19': 'Sakura',
            '20': 'Minji',
            '21': 'Lulu',
            '22': 'Bente',
            '23': 'Ania',
            '24': 'Marcia',
            '25': 'Celia',
            '26': 'Alyona',
            '27': 'Biera',
            '28': 'Ines',
            '29': 'Rodrigo',
            '30': 'Elin',
            '31': 'Samuel',
            '32': 'Kal',
            '33': 'Mia',
            '34': 'Ipek',

            # Here this is clearer:
            'MyLanguages': language_code,
            'MySelectedVoice': voice,
            'MyTextForTTS': text,
            'agreeterms': 'on',
            't': '1',  # Don't know about that one.
            'SendToVaaS': '',
        }

        response = await self._http_session.post(target, data=data)

        results = _MP3_REGEX.search(response.text)
        if results is None:
            raise NeedsUpdateError("Could not extract mp3 url pattern. "
                                   "Check the language or the voice name.")

        return results.group(1)


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

    def get_mp3_url(self, language, voice, text):
        """Retrieve the mp3 url associated to the settings.

        To see the list of supported languages, check the `language` module.

        Args:
            language (str): The language to use for the acapela.
            voice (str): The voice name to use for the acapela.
            text (str): the text to translate to speech.

        Raises:
            NeedsUpdateError: The module needs an update since the mp3
                url could not have been extracted, somehow.

        Returns:
            str: An HTTP url pointing to the generated mp3.

        """
        try:
            language_code = LANGUAGES[language.upper()]
        except KeyError:
            raise LanguageNotSupportedError(
                "The language {} is not supported.".format(language))

        target = self.build_url(
            "demo-tts/DemoHTML5Form_V2.php?langdemo=Powered+by+"
            "<a+href=\"http://www.acapela-vaas.com\">Acapela+Vo"
            "ice+as+a+Service</a>.+For+demo+and+evaluation+purp"
            "ose+only,+for+commercial+use+of+generated+sound+fi"
            "les+please+go+to+<a+href=\"http://www.acapela-box."
            "com\">www.acapela-box.com</a>")

        # What is that for?!
        data = {
            '0': 'Leila',
            '1': 'Laia',
            '2': 'Eliska',
            '3': 'Mette',
            '4': 'Zoe',
            '5': 'Jasmijn',
            '6': 'Tyler',
            '7': 'Deepa',
            '8': 'Rhona',
            '9': 'Rachel',
            '10': 'Sharon',
            '11': 'Hanna',
            '12': 'Sanna',
            '13': 'Manon-be',
            '14': 'Louise',
            '16': 'Claudia',
            '17': 'Dimitris',
            '18': 'Fabiana',
            '19': 'Sakura',
            '20': 'Minji',
            '21': 'Lulu',
            '22': 'Bente',
            '23': 'Ania',
            '24': 'Marcia',
            '25': 'Celia',
            '26': 'Alyona',
            '27': 'Biera',
            '28': 'Ines',
            '29': 'Rodrigo',
            '30': 'Elin',
            '31': 'Samuel',
            '32': 'Kal',
            '33': 'Mia',
            '34': 'Ipek',

            # Here this is clearer:
            'MyLanguages': language_code,
            'MySelectedVoice': voice,
            'MyTextForTTS': text,
            'agreeterms': 'on',
            't': '1',  # Don't know about that one.
            'SendToVaaS': '',
        }

        response = self._http_session.post(target, data=data)

        results = _MP3_REGEX.search(response.text)
        if results is None:
            raise NeedsUpdateError("Could not extract mp3 url pattern. "
                                   "Check the language or the voice name.")

        return results.group(1)

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
            AcapelaGroupError: something went wrong while authenticating.

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
        if response.text == \
                ("You have been locked out due to "
                 "too many invalid login attempts."):
            raise TooManyInvalidLoginAttemptsError(
                "Looks like you are screwed because of too many login "
                "attempts. Try with another IP maybe.")

        try:
            location = response.headers["Location"]
        except KeyError as exn:
            raise NeedsUpdateError(
                "Could not get Location header from login. "
                "The module might need an update.") from exn
        else:
            parse_result = urlparse(location)

            if parse_result.path == '/login/' and \
                    parse_result.query == 'the_error=incorrect_password':
                raise InvalidCredentialsError(
                    "Wrong couple of login/password.")

            # Go to the index to simulate the Location.
            self._http_session.get(location)
