from http import HTTPStatus
import copy

from pytils.translit import slugify as pytils_slugify

from notes.models import Note

from .base import ADD_URL, delete_url, edit_url, LOGIN_URL, BaseTestData


class TestNoteLogic(BaseTestData):

    form_data = {
        'title': 'Новая заметка',
        'text': 'Текст новой заметки',
        'slug': 'novaya-zametka'
    }

    def test_logged_in_user_can_create_note(self):
        """Тестирует, что залогиненный пользователь может создать заметку."""
        form_data = copy.deepcopy(self.form_data)
        response = self.client_user1.post(ADD_URL, data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        created_note = Note.objects.get(slug=form_data['slug'])

        self.assertEqual(created_note.title, form_data['title'])
        self.assertEqual(created_note.text, form_data['text'])
        self.assertEqual(created_note.slug, form_data['slug'])
        self.assertEqual(created_note.author, self.user1)

    def test_anonymous_user_cannot_create_note(self):
        """Тестирует, что анонимный пользователь не может создать заметку."""
        form_data = copy.deepcopy(self.form_data)
        url = ADD_URL
        response = self.client_anonymous.post(url, data=form_data)
        self.assertRedirects(response, f'{LOGIN_URL}?next={url}')
        self.assertEqual((Note.objects
                          .filter(slug=form_data['slug'],
                                  title=form_data['title'],
                                  text=form_data['text'])
                          .count()), 0)

    def test_cannot_create_two_notes_with_same_slug(self):
        """Тестирует, что нельзя создать две заметки с одинаковым slug."""
        form_data = copy.deepcopy(self.form_data)
        same_slug = self.note1.slug
        self.assertTrue(Note.objects.filter(slug=same_slug).exists())
        form_data['slug'] = same_slug
        self.client_user1.post(ADD_URL, data=form_data)
        self.assertEqual(
            Note.objects.filter(slug=same_slug).count(), 1
        )

    def test_slug_is_generated_if_not_provided(self):
        """
        Тестирует, что slug генерируется автоматически,
        если его не заполнить.
        """
        form_data = copy.deepcopy(self.form_data)
        form_data['slug'] = ''
        response = self.client_user1.post(ADD_URL, data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        note = Note.objects.get(title=form_data['title'])
        expected_slug = pytils_slugify(form_data['title'])

        self.assertEqual(note.slug, expected_slug)
        self.assertEqual(note.text, form_data['text'])
        self.assertEqual(note.author, self.user1)

    def test_user_can_edit_own_note(self):
        """
        Тестирует, что пользователь может
        редактировать и удалять свои заметки.
        """
        form_data = copy.deepcopy(self.form_data)
        form_data['slug'] = self.note1.slug
        self.client_user1.post(edit_url(self.note1.slug), data=form_data)

        self.note1.refresh_from_db()

        self.assertEqual(self.note1.author, self.user1)
        self.assertEqual(self.note1.title, form_data['title'])
        self.assertEqual(self.note1.text, form_data['text'])
        self.assertEqual(self.note1.slug, form_data['slug'])

    def test_user_can_delete_own_note(self):
        """
        Тестирует, что пользователь может
        редактировать и удалять свои заметки.
        """
        self.assertEqual(self.note1.author, self.user1)
        self.client_user1.post(delete_url(self.note1.slug),
                               {'title': self.note1.title,
                                'text': self.note1.text,
                                'slug': self.note1.slug})
        self.assertFalse(Note.objects.filter
                         (id=self.note1.id).exists()
                         )

    def test_user_cannot_edit_others_note(self):
        """
        Тестирует, что пользователь не может
        редактировать или удалять чужие заметки.
        """
        form_data = copy.deepcopy(self.form_data)
        response = self.client_user2.post(edit_url(self.note1.slug),
                                          data=form_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.note1.refresh_from_db()

        self.assertEqual(self.note1.author, self.user1)
        self.assertNotEqual(self.note1.title, form_data['title'])
        self.assertNotEqual(self.note1.text, form_data['text'])
        self.assertNotEqual(self.note1.slug, form_data['slug'])

    def test_user_cannot_delete_others_note(self):
        """
        Тестирует, что пользователь не может
        редактировать или удалять чужие заметки.
        """
        self.assertEqual(self.note1.author, self.user1)
        response = self.client_user2.post(delete_url(self.note1.slug),
                                          {'title': self.note1.title,
                                           'text': self.note1.text,
                                           'slug': self.note1.slug})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter
                        (id=self.note1.id).exists()
                        )
