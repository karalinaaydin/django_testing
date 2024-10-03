import pytest

from django.conf import settings

from news.forms import CommentForm
from news.models import Comment


pytestmark = pytest.mark.django_db


def test_max_news_count_on_homepage(client, news_items, urls):
    """
    Тестирует, что на главной странице
    показывается не более 10 новостных элементов.
    """
    url = urls['home']
    response = client.get(url)
    assert len(response.context['object_list']) == (settings
                                                    .NEWS_COUNT_ON_HOME_PAGE)


def test_news_sorted_by_pub_date_desc(client, urls):
    """
    Тестирует, что новости отсортированы
    от самых новых к самым старым на главной странице.
    """
    url = urls['home']
    response = client.get(url)
    news_objects = response.context['object_list']
    news_dates = [news.date for news in news_objects]
    assert [news.date for news in news_objects] == (sorted
                                                    (news_dates, reverse=True)
                                                    )


def test_comments_sorted_by_creation_asc(client, news, comments, urls):
    """
    Тестирует, что комментарии на странице новости отсортированы
    по возрастанию времени создания.
    """
    url = urls['news_detail']
    Comment.objects.filter(news=news).delete()
    Comment.objects.bulk_create(comments)
    response = client.get(url)
    comments_from_context = response.context['news'].comment_set.all()

    dates_from_context = [comment.created for comment in comments_from_context]
    expected_dates = sorted([comment.created for comment in comments])

    assert dates_from_context == expected_dates


def test_comment_form_visible_for_authorized_client(author_client, news, urls):
    """
    Тестирует, что форма комментариев
    доступна для авторизованных пользователей.
    """
    url = urls['news_detail']
    response = author_client.get(url)

    form = response.context.get('form')
    assert form is not None
    assert isinstance(form, CommentForm)


def test_comment_form_not_visible_for_anonymous_client(client, news, urls):
    """
    Тестирует, что форма комментариев недоступна
    для анонимных пользователей.
    """
    url = urls['news_detail']
    response = client.get(url)

    assert 'form' not in response.context
