import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    'name, expected_count',
    (
        ('notes:home', 10),
    )
)
def test_homepage_shows_maximum_of_10_news(client, name, expected_count):
    """
    Тестирует, что на главной странице
    показывается не более 10 новостных элементов.
    """
    url = reverse(name)
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == expected_count


def test_news_sorted_by_pub_date_desc(client):
    """
    Тестирует, что новости отсортированы
    от самых новых к самым старым на главной странице.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_dates = [news.date for news in object_list]
    assert news_dates == sorted(news_dates, reverse=True)


def test_comments_sorted_by_creation_asc(client, news):
    """
    Тестирует, что комментарии на странице новости отсортированы
    по возрастанию времени создания.
    """
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    comment_set = response.context['comment_set']
    comment_dates = [comment.created for comment in comment_set]
    assert comment_dates == sorted(comment_set)


@pytest.mark.parametrize(
    'client_fixture, form_expected',
    (
        (pytest.lazy_fixture('not_author'), False),
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), True)
    )
)
def test_comment_form_visibility(client_fixture, request, news, form_expected):
    """
    Тестирует, что форма комментариев доступна для авторизованных
    пользователей и недоступна для анонимных.
    """
    client = request.getfixturevalue(client_fixture)
    url = reverse('news:detail', args=[news.id])

    response = client.get(url)

    if form_expected:
        assert 'form' in response.context
    else:
        assert 'form' not in response.context
