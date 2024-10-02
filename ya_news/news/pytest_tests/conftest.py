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
def news_items(db):
    for i in range(10):
        News.objects.create(
            title=f'Заголовок новости {i}',
            text=f'Текст новости {i}',
        )


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст тестового комментария',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def comments(news, author):
    comments = [
        Comment.objects.create(text='Первый комментарий', news=news,
                               author=author, created='2024-01-01 10:00:00'),
        Comment.objects.create(text='Второй комментарий', news=news,
                               author=author, created='2024-01-01 12:00:00'),
        Comment.objects.create(text='Третий комментарий', news=news,
                               author=author, created='2024-01-01 14:00:00'),
    ]
    return comments


@pytest.fixture
def form_data():
    return {
        'text': 'Текст комментария',
    }
