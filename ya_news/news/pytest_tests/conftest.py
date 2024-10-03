import time

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Тестовая новость',
        text='Содержание тестовой новости',
    )


@pytest.fixture
def news_items(db):
    return News.objects.bulk_create(
        [
            News(title=f'Заголовок новости {i}', text=f'Текст новости {i}')
            for i in range(settings.NEWS_COUNT_ON_HOME_PAGE)
        ]
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        text='Текст тестового комментария',
        author=author,
        news=news)


@pytest.fixture
def comments(news, author):
    comments_list = []
    for i in range(1, 333):
        comment = Comment(
            text=f'Комментарий {i}',
            news=news,
            author=author,
        )
        comments_list.append(comment)
        time.sleep(0.01)

    return comments_list


@pytest.fixture
def clear_comments(news):
    Comment.objects.all().delete()
    yield


@pytest.fixture
def urls(news, comment):
    """Фикстура для предварительного вычисления URL-адресов для тестов."""
    return {
        'home': reverse('news:home'),
        'news_detail': reverse('news:detail', args=[news.id]),
        'edit': reverse('news:edit', args=[comment.id]),
        'delete': reverse('news:delete', args=[comment.id]),
        'login': reverse('users:login'),
        'logout': reverse('users:logout'),
        'signup': reverse('users:signup'),
    }
