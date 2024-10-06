import pytest
from http import HTTPStatus

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url',
    [
        pytest.lazy_fixture('login_url'),
        pytest.lazy_fixture('logout_url'),
        pytest.lazy_fixture('home_url'),
        pytest.lazy_fixture('signup_url'),
        pytest.lazy_fixture('news_detail_url')
    ]
)
def test_pages_availability_for_anonymous_user(client, url):
    """Тестирует доступность страниц для анонимного пользователя."""
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    )
)
@pytest.mark.parametrize(
    'url',
    [
        pytest.lazy_fixture('delete_url'),
        pytest.lazy_fixture('edit_url'),
    ]
)
def test_pages_availability_for_different_users(expected_status, url,
                                                parametrized_client):
    """Тестирует доступность страниц для разных пользователей."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    [
        pytest.lazy_fixture('delete_url'),
        pytest.lazy_fixture('edit_url'),
    ]
)
def test_redirects_for_anonymous_user(client, redirect_url, url):
    """Тестирует редиректы для анонимного пользователя."""
    expected_url = redirect_url(url)
    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url
