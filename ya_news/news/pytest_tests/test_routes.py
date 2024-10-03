import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name',
    ('home', 'login', 'logout', 'signup', 'news_detail')
)
def test_pages_availability_for_anonymous_user(client, name, urls):
    """
    Тестирует доступность страниц для анонимного пользователя.
    """
    url = urls[name]
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
    'name',
    ('delete', 'edit'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, expected_status, urls
):
    """
    Тестирует доступность страниц для разных пользователей.
    """
    url = urls[name]
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('delete', 'edit'),
)
def test_redirects_for_anonymous_user(client, name, news, urls):
    """
    Тестирует редиректы для анонимного пользователя.
    """
    login_url = urls['login']
    url = urls[name]
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
