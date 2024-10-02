from http import HTTPStatus

import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment(client, news, form_data):
    """
    Анонимный пользователь не может отправить комментарий
    на странице новости.
    """
    url = reverse('news:detail', args=[news.id])
    response = client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert not (Comment.objects
                .filter(text=form_data['text'], news=news)
                .exists())


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(author_client, news, form_data):
    """
    Авторизованный пользователь может отправить комментарий
    на странице новости.
    """
    url = reverse('news:detail', args=[news.id])
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert (Comment.objects
            .filter(text=form_data['text'], news=news)
            .exists())


@pytest.mark.django_db
@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_forbidden_words_not_published(author_client, news,
                                                    bad_word, form_data):
    """
    Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    form_data['text'] = f'Этот комментарий содержит слово: {bad_word}'
    url = reverse('news:detail', args=[news.id])
    response = author_client.post(url, data=form_data)
    assert WARNING in response.content.decode('utf-8')
    assert not (Comment.objects
                .filter(text=form_data['text'], news=news)
                .exists())


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_user_can_delete_own_comment(author_client, comment, name):
    """
    Авторизованный пользователь может
    удалять и редактировать свои комментарии.
    """
    url = reverse(name, args=[comment.id])
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_user_cannot_delete_another_users_comment(not_author_client,
                                                  comment, name):
    """
    Авторизованный пользователь не может удалять
    и редактировать чужие комментарии.
    """
    url = reverse(name, args=[comment.id])
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(id=comment.id).exists()
