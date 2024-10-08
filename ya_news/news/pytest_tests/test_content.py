import pytest

from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_max_news_count_on_homepage(client, news_items, home_url):
    """
    Тестирует, что на главной странице
    показывается не более 10 новостных элементов.
    """
    assert len(client.get(home_url).
               context['object_list']) == (settings.NEWS_COUNT_ON_HOME_PAGE)


def test_news_sorted_by_pub_date_desc(client, home_url):
    """
    Тестирует, что новости отсортированы
    от самых новых к самым старым на главной странице.
    """
    news_objects = client.get(home_url).context['object_list']
    news_dates = [news.date for news in news_objects]
    assert news_dates == (sorted
                          (news_dates, reverse=True)
                          )


def test_comments_sorted_by_creation_asc(client, news, comments,
                                         news_detail_url):
    """
    Тестирует, что комментарии на странице новости отсортированы
    по возрастанию времени создания.
    """
    response = client.get(news_detail_url)
    comments_from_context = response.context['news'].comment_set.all()

    dates_from_context = [comment.created for comment in comments_from_context]
    expected_dates = sorted(dates_from_context)

    assert dates_from_context == expected_dates


def test_comment_form_visible_for_authorized_client(author_client, news,
                                                    news_detail_url):
    """
    Тестирует, что форма комментариев
    доступна для авторизованных пользователей.
    """
    assert isinstance(author_client.get(news_detail_url).context.get('form'),
                      CommentForm)


def test_comment_form_not_visible_for_anonymous_client(client, news,
                                                       news_detail_url):
    """
    Тестирует, что форма комментариев недоступна
    для анонимных пользователей.
    """
    assert 'form' not in client.get(news_detail_url).context
