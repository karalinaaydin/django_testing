import pytest

from django.test.client import Client

from news.models import News, Comment


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
def comment(author):
    comment = Comment.objects.create(
        text='Текст тестового комментария',
        author=author_client.user,
        news=news
    )
    return comment


@pytest.fixture
def form_data():
    return {
        'text': 'Текст комментария',
    }
