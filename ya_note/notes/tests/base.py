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

def detail_url(slug):
    return reverse('notes:detail', args=[slug])

def delete_url(slug):
    return reverse('notes:delete', args=[slug])

def edit_url(slug):
    return reverse('notes:edit', args=[slug])


class BaseTestData(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для всех тестов."""
        cls.user1 = User.objects.create(username='Лев Толстой')
        cls.user2 = User.objects.create(username='Фёдор Достоевский')
        cls.note1 = Note.objects.create(title='Заметка 1',
                                        text='Текст 1',
                                        author=cls.user1)
        cls.note2 = Note.objects.create(title='Заметка 2',
                                        text='Текст 2',
                                        author=cls.user2)

    def setUp(self):
        """Настройка клиента для авторизованных пользователей."""
        self.client_user1 = self.client_class()
        self.client_user1.force_login(self.user1)

        self.client_user2 = self.client_class()
        self.client_user2.force_login(self.user2)

        self.client_anonymous = self.client_class()
