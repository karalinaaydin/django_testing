import pytest
from http import HTTPStatus

pytestmark = pytest.mark.django_db

DELETE_URL = pytest.lazy_fixture('delete_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
HOME_URL = pytest.lazy_fixture('home_url')
NEWS_DETAIL_URL = pytest.lazy_fixture('news_detail_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')

DELETE_REDIRECT_URL = pytest.lazy_fixture('delete_redirect_url')
EDIT_REDIRECT_URL = pytest.lazy_fixture('edit_redirect_url')

ANONYMOUS = pytest.lazy_fixture('client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')

@pytest.mark.parametrize(
    'parametrized_client, url, expected_status',
    (
        (ANONYMOUS, LOGIN_URL, HTTPStatus.OK),
        (ANONYMOUS, LOGOUT_URL, HTTPStatus.OK),
        (ANONYMOUS, HOME_URL, HTTPStatus.OK),
        (ANONYMOUS, SIGNUP_URL, HTTPStatus.OK),
        (ANONYMOUS, NEWS_DETAIL_URL, HTTPStatus.OK),

        (NOT_AUTHOR_CLIENT, DELETE_URL, HTTPStatus.NOT_FOUND),
        (NOT_AUTHOR_CLIENT, EDIT_URL, HTTPStatus.NOT_FOUND),
        (AUTHOR_CLIENT, DELETE_URL, HTTPStatus.OK),
        (AUTHOR_CLIENT, EDIT_URL, HTTPStatus.OK),

        (ANONYMOUS, DELETE_URL, HTTPStatus.FOUND),
        (ANONYMOUS, EDIT_URL, HTTPStatus.FOUND),
        )
        )
def test_pages_availability_for_different_users(expected_status, url,
                                                parametrized_client):
    """Тестирует доступность страниц для разных пользователей."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, expected_url',
    [
        (DELETE_URL, DELETE_REDIRECT_URL),
        (EDIT_URL, EDIT_REDIRECT_URL)
    ]
)
def test_redirects_for_anonymous_user(client, expected_url, url):
    """Тестирует редиректы для анонимного пользователя."""
    response = client.get(url)
    assert response.url == expected_url
