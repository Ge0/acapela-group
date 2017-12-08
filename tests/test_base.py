from unittest.mock import MagicMock, patch

import pytest

from acapela_group.base import (AcapelaGroup, InvalidCredentialsError,
                                NeedsUpdateError)


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

    with patch('requests.sessions.Session.post') as post_method:
        post_method.return_value = invalid_credentials_mock
        with pytest.raises(InvalidCredentialsError):
            acapela.authenticate("foo", "bar")

        post_method.return_value = needs_update_credentials_mock
        with pytest.raises(NeedsUpdateError):
            acapela.authenticate("foo", "bar")

        with patch('requests.sessions.Session.get') as get_method:
            post_method.return_value = success_mock
            get_method.return_value = None  # Just mock the get() call.

            # Should run without any trouble!
            acapela.authenticate("foo", "bar")
