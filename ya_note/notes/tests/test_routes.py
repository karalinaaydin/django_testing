from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для всех тестов."""
        cls.note = Note.objects.create(title='Заголовок', text='Текст')
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')

    def test_pages_availability(self):
        """
        Проверяет доступность основных страниц для анонимных пользователей.
        """
        urls = (
            ('notes:home', None),
            ('notes:detail', (self.note.slug,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """
        Проверяет, что анонимные пользователи
        перенаправляются на страницу входа.
        """
        login_url = reverse('users:login')
        urls = (('notes:list', None),
                ('notes:success', None),
                ('notes:detail', (self.note.slug,)),
                ('notes:add', None),
                ('notes:edit', (self.note.slug,)),
                ('notes:delete', (self.note.slug,))
                )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_note_detail_edit_delete(self):
        """
        Проверяет доступность страниц просмотра,
        редактирования и удаления заметок для авторов и других пользователей.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            urls = (
                ('notes:detail', (self.note.slug,)),
                ('notes:edit', (self.note.slug,)),
                ('notes:delete', (self.note.slug,)),
            )
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_for_note_list_success_and_create(self):
        """
        Проверяет доступность страниц списка, успешного добавления
        и создания для авторизованного пользователя.
        """
        self.client.force_login(self.reader)
        for name in ('notes:list',
                     'notes:success',
                     'notes:add',):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
