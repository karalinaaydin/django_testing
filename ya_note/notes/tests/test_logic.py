from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from notes.models import Note
from pytils.translit import slugify as pytils_slugify

User = get_user_model()


class TestNoteLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создаёт тестовые данные для тестов."""
        cls.user1 = User.objects.create(username='Лев Толстой')
        cls.user2 = User.objects.create(username='Фёдор Достоевский')
        cls.note = Note.objects.create(title='Заметка 1',
                                       text='Текст 1',
                                       author=cls.user1)

    def test_logged_in_user_can_create_note(self):
        """Тестирует, что залогиненный пользователь может создать заметку."""
        self.client.force_login(self.user1)
        url = reverse('notes:add')
        data = {'title': 'Новая заметка', 'text': 'Текст заметки'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Note.objects.filter(title='Новая заметка').exists())

    def test_anonymous_user_cannot_create_note(self):
        """Тестирует, что анонимный пользователь не может создать заметку."""
        url = reverse('notes:add')
        data = {'title': 'Заметка от анонима', 'text': 'Текст заметки'}
        response = self.client.post(url, data)
        login_url = reverse('users:login')
        self.assertRedirects(response, f'{login_url}?next={url}')
        self.assertFalse(Note.objects.filter
                         (title='Заметка от анонима').exists()
                         )

    def test_cannot_create_two_notes_with_same_slug(self):
        """Тестирует, что нельзя создать две заметки с одинаковым slug."""
        SAME_SLUG = 'zametka_1'
        self.client.force_login(self.user1)
        Note.objects.create(
            title='Заметка 1',
            text='Текст 1',
            slug=SAME_SLUG,
            author=self.user1
        )
        self.assertTrue(Note.objects.filter(slug='zametka-1').exists())
        with self.assertRaises(IntegrityError):
            Note.objects.create(title='Заметка 1 (дубликат)',
                                text='Текст дубликата',
                                slug=SAME_SLUG,
                                author=self.user1)

    def test_slug_is_generated_if_not_provided(self):
        """
        Тестирует, что slug генерируется автоматически,
        если его не заполнить.
        """
        self.client.force_login(self.user1)
        url = reverse('notes:add')
        data = {'title': 'Заголовок без slug', 'text': 'Текст заметки'}
        self.client.post(url, data)
        note = Note.objects.get(title='Заголовок без slug')
        expected_slug = pytils_slugify('Заголовок без slug')
        self.assertEqual(note.slug, expected_slug)

    def test_user_can_edit_and_delete_own_note(self):
        """
        Тестирует, что пользователь может
        редактировать и удалять свои заметки.
        """
        upd_title = 'Обновлённая заметка'
        self.client.force_login(self.user1)
        self.assertEqual(self.note.author, self.user1)

        edit_url = reverse('notes:edit', args=[self.note.slug])
        self.client.post(edit_url, {'title': upd_title,
                                    'text': 'Обновлённый текст'})
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, upd_title)

        delete_url = reverse('notes:delete', args=[self.note.slug])
        self.client.post(delete_url)
        self.assertFalse(Note.objects.filter
                         (id=self.note.id).exists()
                         )

    def test_user_cannot_edit_or_delete_others_note(self):
        """
        Тестирует, что пользователь не может
        редактировать или удалять чужие заметки.
        """
        self.client.force_login(self.user2)

        edit_url = reverse('notes:edit', args=[self.note.slug])
        response = self.client.post(edit_url, {'title': 'Неверная правка',
                                               'text': 'Неверный текст'})
        self.assertEqual(response.status_code, 404)

        delete_url = reverse('notes:delete', args=[self.note.slug])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
