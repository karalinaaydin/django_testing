import pytest
from http import HTTPStatus

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


FORM_DATA = {
    'text': 'Текст комментария',
}


def test_anonymous_user_cannot_post_comment(client, news, news_detail_url):
    """
    Анонимный пользователь не может отправить комментарий
    на странице новости.
    """
    Comment.objects.all().delete()
    response = client.post(news_detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(news=news).count() == 0


def test_authenticated_user_can_post_comment(author_client, author,
                                             news, news_detail_url):
    """
    Авторизованный пользователь может отправить комментарий
    на странице новости.
    """
    Comment.objects.all().delete()
    response = author_client.post(news_detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1

    comment = Comment.objects.first()
    assert comment.author == author
    assert comment.news == news
    assert comment.text == FORM_DATA['text']


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_forbidden_words_not_published(author_client, news,
                                                    bad_word, news_detail_url):
    """
    Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    Comment.objects.all().delete()
    response = author_client.post(news_detail_url,
                                  data={
                                      'text': f'Текст комментария: {bad_word}'}
                                  )
    form = response.context['form']

    assert 'text' in form.errors
    assert WARNING in form.errors['text']
    assert Comment.objects.count() == 0


def test_user_can_delete_own_comment(comment, author_client, delete_url):
    """
    Авторизованный пользователь может
    удалять свои комментарии.
    """
    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(id=comment.id).exists()


def test_user_can_edit_own_comment(comment, author_client, edit_url):
    """
    Авторизованный пользователь может
    редактировать свои комментарии.
    """
    response = author_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    updated_comment = Comment.objects.get(id=comment.id)

    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_user_cannot_delete_another_users_comment(comment, not_author_client,
                                                  delete_url):
    """
    Авторизованный пользователь не может
    удалять комментарии других пользователей.
    """
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)

    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author
    assert comment_from_db.text == comment.text


def test_user_cannot_edit_another_users_comment(comment, not_author_client,
                                                edit_url):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = not_author_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)

    assert comment_from_db.text == comment.text
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author
