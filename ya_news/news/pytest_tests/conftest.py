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
        News(title=f'Заголовок новости {i}', text=f'Текст новости {i}')
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE)
        )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        text='Текст тестового комментария',
        author=author,
        news=news)


@pytest.fixture
def comments(news, author):
    Comment.objects.bulk_create(
        Comment(
            text=f'Комментарий {i}',
            news=news,
            author=author,
        )
        for i in range(1, 333)
    )
    return Comment.objects.filter(news=news)


@pytest.fixture
def home_url():
    """Фикстура для получения URL домашней страницы."""
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    """Фикстура для получения URL деталей новости."""
    return reverse('news:detail', args=[news.id])


@pytest.fixture
def edit_url(comment):
    """Фикстура для получения URL редактирования комментария."""
    return reverse('news:edit', args=[comment.id])


@pytest.fixture
def delete_url(comment):
    """Фикстура для получения URL удаления комментария."""
    return reverse('news:delete', args=[comment.id])


@pytest.fixture
def login_url():
    """Фикстура для получения URL страницы входа."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """Фикстура для получения URL страницы выхода."""
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    """Фикстура для получения URL страницы регистрации."""
    return reverse('users:signup')


@pytest.fixture
def redirect_url(login_url):
    """Фикстура для формирования ожидаемого URL редиректа."""
    def _redirect(url):
        return f'{login_url}?next={url}'
    return _redirect
