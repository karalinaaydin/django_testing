from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
HOME_PAGE_URL = reverse('notes:home')
ADD_URL = reverse('notes:add')
REDIRECT_ADD_URL = f'{LOGIN_URL}?next={ADD_URL}'
LIST_URL = reverse('notes:list')
REDIRECT_LIST_URL = f'{LOGIN_URL}?next={LIST_URL}'
SUCCESS_URL = reverse('notes:success')
REDIRECT_SUCCESS_URL = f'{LOGIN_URL}?next={SUCCESS_URL}'

NOTE_SLUG = 'Zametka-1'
DETAIL_URL = reverse('notes:detail', args=[NOTE_SLUG])
REDIRECT_DETAIL_URL = f'{LOGIN_URL}?next={DETAIL_URL}'
DELETE_URL = reverse('notes:delete', args=[NOTE_SLUG])
REDIRECT_DELETE_URL = f'{LOGIN_URL}?next={DELETE_URL}'
EDIT_URL = reverse('notes:edit', args=[NOTE_SLUG])
REDIRECT_EDIT_URL = f'{LOGIN_URL}?next={EDIT_URL}'


def get_redirect_url(url):
    return f'{LOGIN_URL}?next={url}'


class BaseTestData(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для всех тестов."""
        super().setUp(cls)

        cls.user1 = User.objects.create(username='Лев Толстой')
        cls.user2 = User.objects.create(username='Фёдор Достоевский')
        cls.note1 = Note.objects.create(title='Заметка 1',
                                        text='Текст 1',
                                        slug='Zametka-1',
                                        author=cls.user1)
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'novaya-zametka'}

        cls.client_user1 = cls.client_class()
        cls.client_user1.force_login(cls.user1)

        cls.client_user2 = cls.client_class()
        cls.client_user2.force_login(cls.user2)

        cls.client_anonymous = cls.client_class()
