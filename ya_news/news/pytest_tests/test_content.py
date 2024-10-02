import pytest
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, expected_count',
    (
        ('news:home', 10),
    )
)
def test_homepage_shows_maximum_of_10_news(client, name,
                                           expected_count, news_items):
    """
    Тестирует, что на главной странице
    показывается не более 10 новостных элементов.
    """
    url = reverse(name)
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == expected_count


@pytest.mark.django_db
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


def test_comments_sorted_by_creation_asc(client, news, comments):
    """
    Тестирует, что комментарии на странице новости отсортированы
    по возрастанию времени создания.
    """
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    comments_from_context = response.context['news'].comment_set.all()
    comment_dates_from_context = [comment.created
                                  for comment in comments_from_context
                                  ]
    expected_comment_dates = sorted([comment.created for comment in comments])
    assert comment_dates_from_context == expected_comment_dates


@pytest.mark.parametrize(
    'parametrized_client, form_expected',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), True)
    )
)
def test_comment_form_visibility(parametrized_client, request,
                                 news, form_expected):
    """
    Тестирует, что форма комментариев доступна для авторизованных
    пользователей и недоступна для анонимных.
    """
    url = reverse('news:detail', args=[news.id])

    response = parametrized_client.get(url)

    if form_expected:
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
    else:
        assert 'form' not in response.context
