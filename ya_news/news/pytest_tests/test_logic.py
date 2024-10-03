from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


FORM_DATA = {
    'text': 'Текст комментария',
}


def test_anonymous_user_cannot_post_comment(client, news, urls):
    """
    Анонимный пользователь не может отправить комментарий
    на странице новости.
    """
    url = urls['news_detail']
    Comment.objects.filter(news=news).delete()
    response = client.post(url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(news=news).count() == 0


def test_authenticated_user_can_post_comment(author_client, author, news, urls):

    """
    Авторизованный пользователь может отправить комментарий
    на странице новости.
    """
    url = urls['news_detail']
    Comment.objects.filter(news=news).delete()
    response = author_client.post(url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(news=news).count() == 1

    comment = Comment.objects.first()
    assert comment.author == author
    assert comment.news == news
    assert comment.text == FORM_DATA['text']


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_forbidden_words_not_published(author_client, news,
                                                    bad_word, urls):
    """
    Если комментарий содержит запрещённые слова, он не будет опубликован, 
    а форма вернёт ошибку. 
    """
    Comment.objects.filter(news=news).delete()
    FORM_DATA['text'] = f'Этот комментарий содержит слово: {bad_word}'
    url = urls['news_detail']
    response = author_client.post(url, data=FORM_DATA)

    assert WARNING in response.content.decode('utf-8')
    assert Comment.objects.filter(news=news).count() == 0


def test_user_can_delete_own_comment(comment, author_client, urls):

    """
    Авторизованный пользователь может
    удалять свои комментарии.
    """
    url = urls['delete']
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(id=comment.id,
                                      news=comment.news,
                                      author=comment.author,
                                      text=comment.text).exists()


def test_user_can_edit_own_comment(comment, author_client, urls):

    """
    Авторизованный пользователь может
    редактировать свои комментарии.
    """
    url = urls['edit']
    new_text = 'Обновленный текст комментария'
    response = author_client.post(url, data={'text': new_text})
    assert response.status_code == HTTPStatus.FOUND

    comment.refresh_from_db()
    assert comment.text == new_text


def test_user_cannot_delete_another_users_comment(comment, not_author_client,
                                                  urls):

    """
    Авторизованный пользователь не может
    удалять комментарии других пользователей.
    """
    url = urls['delete']
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(id=comment.id,
                                  news=comment.news,
                                  author=comment.author,
                                  text=comment.text).exists()


def test_user_cannot_edit_another_users_comment(comment, not_author_client,
                                                urls):

    """
    Авторизованный пользователь может
    редактировать свои комментарии.
    """
    url = urls['edit']
    new_text = 'Обновленный текст комментария'
    response = not_author_client.post(url, data={'text': new_text})
    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()
    assert comment.text != new_text
