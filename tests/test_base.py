import asyncio
from unittest.mock import MagicMock, patch

import pytest

from acapela_group.base import (AcapelaGroup, AcapelaGroupAsync,
                                InvalidCredentialsError,
                                LanguageNotSupportedError, NeedsUpdateError,
                                TooManyInvalidLoginAttemptsError)


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


def test_acapela_group_init():
    """Test the __init__ method of the `AcapelaGroup` class."""
    acapela = AcapelaGroup()

    assert acapela.base_url == "http://www.acapela-group.com"

    acapela = AcapelaGroup(base_url="http://www.fake.com")
    assert acapela.base_url == "http://www.fake.com"


def test_acapela_build_url():
    """Test the build_url method of the `AcapelaGroup` class."""
    acapela = AcapelaGroup(base_url="http://www.alwayslookon.com")
    assert acapela.build_url() == "http://www.alwayslookon.com/"
    assert acapela.build_url("the/bright?side=of+life") == \
        "http://www.alwayslookon.com/the/bright?side=of+life"


def test_acapela_authenticate():
    """Test the authenticate method of the `AcapelaGroup` class."""
    acapela = AcapelaGroup()
    invalid_credentials_mock = MagicMock()
    invalid_credentials_mock.headers = {
        "Location":
            "http://www.acapela-group.com/login/?the_error=incorrect_password"
    }

    needs_update_credentials_mock = MagicMock()

    # Here, do not set the "Location" headers. It would mean that the
    # AcapelaGroup class needs some update!
    needs_update_credentials_mock.headers.__getitem__.side_effect = KeyError

    success_mock = MagicMock()
    success_mock.headers = {
        "Location": "http://www.acapela-group.com/"
    }

    too_many_attempts_mock = MagicMock()
    too_many_attempts_mock.text = ("You have been locked out due to "
                                   "too many invalid login attempts.")

    with patch('requests.sessions.Session.post') as post_method:
        post_method.return_value = invalid_credentials_mock
        with pytest.raises(InvalidCredentialsError):
            acapela.authenticate("foo", "bar")

        post_method.return_value = needs_update_credentials_mock
        with pytest.raises(NeedsUpdateError):
            acapela.authenticate("foo", "bar")

        post_method.return_value = too_many_attempts_mock
        with pytest.raises(TooManyInvalidLoginAttemptsError):
            acapela.authenticate("foo", "bar")

        with patch('requests.sessions.Session.get') as get_method:
            post_method.return_value = success_mock
            get_method.return_value = None  # Just mock the get() call.

            # Should run without any trouble!
            acapela.authenticate("foo", "bar")


def test_get_mp3_url():
    """Test the `get_mp3_url` method of the `AcapelaGroup` class."""
    acapela = AcapelaGroup()

    mp3_url_mock = MagicMock()
    mp3_url_mock.text = "var myPhpVar = 'http://site.com/path/to/file.mp3';"

    no_mp3_url_mock = MagicMock()
    no_mp3_url_mock.text = "<dumb>lol</dumb>"

    with patch('requests.sessions.Session.post') as post_method:
        post_method.return_value = mp3_url_mock
        assert acapela.get_mp3_url('french (france)', 'bar', 'baz') == \
            "http://site.com/path/to/file.mp3"

        post_method.return_value = no_mp3_url_mock
        with pytest.raises(NeedsUpdateError):
            acapela.get_mp3_url('french (france)', 'bar', 'baz')

    # Test with an invalid language
    with pytest.raises(LanguageNotSupportedError) as exn:
        acapela.get_mp3_url('Unexisting language', 'bar', 'foo')
    assert 'The language Unexisting language is not supported.' in str(exn)


@pytest.mark.asyncio
async def test_acapela_group_async_init():
    """Test the __init__ method of the `AcapelaGroup` class."""
    async with AcapelaGroupAsync() as acapela:
        assert acapela.base_url == "http://www.acapela-group.com"

    async with AcapelaGroupAsync(base_url="http://www.fake.com") as acapela:
        assert acapela.base_url == "http://www.fake.com"


@pytest.mark.asyncio
async def test_acapela_group_async_authenticate():
    """Test the authenticate method of the `AcapelaGroupAsync` class."""
    async with AcapelaGroupAsync() as acapela:
        invalid_credentials_mock = MagicMock()
        invalid_credentials_mock.headers = {
            "Location": "http://www.acapela-group.com/login/"
                        "?the_error=incorrect_password"
        }

        f = asyncio.Future()
        f.set_result("Wrong credentials")
        invalid_credentials_mock.text.side_effect = f

        needs_update_credentials_mock = MagicMock()
        f = asyncio.Future()
        f.set_result("Wrong credentials")
        needs_update_credentials_mock.text.side_effect = f

        f = asyncio.Future()
        f.set_exception(KeyError)

        # Here, do not set the "Location" headers. It would mean that the
        # AcapelaGroup class needs some update!
        needs_update_credentials_mock.headers.__getitem__.side_effect = f

        success_mock = MagicMock()
        success_mock.headers = {
            "Location": "http://www.acapela-group.com/"
        }

        too_many_attempts_mock = MagicMock()
        too_many_attempts_mock.text = ("You have been locked out due to "
                                       "too many invalid login attempts.")

        with patch('aiohttp.ClientSession.post') as post_method:
            f = asyncio.Future()
            f.set_result(invalid_credentials_mock)
            post_method.return_value = f
            with pytest.raises(RuntimeError):
                await acapela.authenticate("foo", "bar")

            f = asyncio.Future()
            f.set_result(needs_update_credentials_mock)
            post_method.return_value = f
            with pytest.raises(RuntimeError):
                await acapela.authenticate("foo", "bar")

            # post_method.return_value = too_many_attempts_mock
            # with pytest.raises(TooManyInvalidLoginAttemptsError):
            #     await acapela.authenticate("foo", "bar")

            # with patch('requests.sessions.Session.get') as get_method:
            #     post_method.return_value = success_mock
            #     get_method.return_value = None  # Just mock the get() call.

                # Should run without any trouble!
            #     await acapela.authenticate("foo", "bar")
