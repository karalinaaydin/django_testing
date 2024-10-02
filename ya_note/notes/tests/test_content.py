from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создаёт тестовые данные для тестов."""
        cls.user1 = User.objects.create(username='Лев Толстой')
        cls.user2 = User.objects.create(username='Фёдор Достоевский')
        cls.note1 = Note.objects.create(title='Заметка 1',
                                        text='Текст 1',
                                        author=cls.user1)
        cls.note2 = Note.objects.create(title='Заметка 2',
                                        text='Текст 2',
                                        author=cls.user2)

    def test_note_in_object_list(self):
        """
        Тестирует, что заметка отображается на странице
        списка заметок в object_list.
        """
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertIn(self.note1, response.context['object_list'])
        self.assertIn(self.note2, response.context['object_list'])

    def test_user_notes_dont_include_other_users_notes(self):
        """
        Тестирует, что в списке заметок пользователя
        не отображаются заметки других пользователей.
        """
        self.client.force_login(self.user1)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertIn(self.note1, response.context['object_list'])
        self.assertNotIn(self.note2, response.context['object_list'])

    def test_creation_page_contains_form(self):
        """
        Тестирует, что на страницах создания и редактирования заметки
        передаются формы.
        """
        self.client.force_login(self.user1)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            )
        for name, args in urls:
            url = reverse(name, args=args)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertTrue(response.context['form'].is_bound is False)
