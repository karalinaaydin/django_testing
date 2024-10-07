from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

ADD_URL = reverse('notes:add')
HOME_PAGE_URL = reverse('notes:home')
LIST_URL = reverse('notes:list')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
SUCCESS_URL = reverse('notes:success')

NOTE_SLUG = 'Zametka-1'
DETAIL_URL = reverse('notes:detail', args=[NOTE_SLUG])
DELETE_URL = reverse('notes:delete', args=[NOTE_SLUG])
EDIT_URL = reverse('notes:edit', args=[NOTE_SLUG])


def get_redirect_url(url):
    return f'{LOGIN_URL}?next={url}'


class BaseTestData(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для всех тестов."""
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

    def setUp(self):
        """Настройка для каждого теста."""
        super().setUp()
        self.form_data = self.get_form_data()

    @staticmethod
    def get_form_data():
        """Метод для получения свежего словаря данных формы."""
        return {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
