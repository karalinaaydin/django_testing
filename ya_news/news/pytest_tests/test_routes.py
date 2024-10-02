from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (('notes:home', None),
     ('users:login', None),
     ('users:logout', None),
     ('users:signup', None),
     )
     )
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

def test_news_detail_page_accessible_for_anonymous_user(client, news):
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status', 
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
     )
     )
@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, news, expected_status
):
    url = reverse(name, args=(news.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_redirects_for_anonymous_user(client, name, news):
    login_url = reverse('users:login')
    url = reverse(name, args=(news.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
