from http import HTTPStatus

from pytils.translit import slugify as pytils_slugify

from notes.models import Note
from .base import (ADD_URL, DELETE_URL, EDIT_URL, BaseTestData,
                   get_redirect_url)


class TestNoteLogic(BaseTestData):

    def test_logged_in_user_can_create_note(self):
        """Тестирует, что залогиненный пользователь может создать заметку."""
        Note.objects.all().delete()
        self.assertFalse(Note.objects
                         .filter(slug=self.form_data['slug']).exists())

        response = self.client_user1.post(ADD_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.all().count(), 1)
        created_note = Note.objects.get(slug=self.form_data['slug'])

        self.assertEqual(created_note.author, self.user1)
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])

    def test_anonymous_user_cannot_create_note(self):
        """Тестирует, что анонимный пользователь не может создать заметку."""
        notes_before = set(Note.objects.values_list('id', flat=True))
        response = self.client_anonymous.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, get_redirect_url(ADD_URL))
        notes_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(notes_before, notes_after)

    def test_cannot_create_two_notes_with_same_slug(self):
        """Тестирует, что нельзя создать две заметки с одинаковым slug."""
        notes_before = set(Note.objects.values_list('id', flat=True))
        self.form_data['slug'] = self.note1.slug
        self.client_user1.post(ADD_URL, data=self.form_data)
        notes_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(notes_before, notes_after)

    def test_slug_is_generated_if_not_provided(self):
        """
        Тестирует, что slug генерируется автоматически,
        если его не заполнить.
        """
        Note.objects.all().delete()
        self.form_data['slug'] = ''
        expected_slug = pytils_slugify(self.form_data['title'])
        self.assertFalse(Note.objects
                         .filter(slug=expected_slug).exists())
        response = self.client_user1.post(ADD_URL, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.all().count(), 1)

        note = Note.objects.get(slug=expected_slug)

        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user1)

    def test_user_can_edit_own_note(self):
        """
        Тестирует, что пользователь может
        редактировать и удалять свои заметки.
        """
        self.client_user1.post(EDIT_URL,
                               data=self.form_data)
        edited_note = Note.objects.get(pk=self.note1.pk)
        self.assertEqual(edited_note.author, self.note1.author)

        self.assertEqual(edited_note.title, self.form_data['title'])
        self.assertEqual(edited_note.text, self.form_data['text'])
        self.assertEqual(edited_note.slug, self.form_data['slug'])

    def test_user_can_delete_own_note(self):
        """
        Тестирует, что пользователь может
        редактировать и удалять свои заметки.
        """
        initial_count = Note.objects.count()

        self.assertTrue(Note.objects.filter(id=self.note1.id).exists())
        self.client_user1.post(DELETE_URL)
        self.assertFalse(Note.objects.filter(id=self.note1.id).exists())

        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_user_cannot_edit_others_note(self):
        """
        Тестирует, что пользователь не может
        редактировать или удалять чужие заметки.
        """
        response = self.client_user2.post(EDIT_URL, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note = Note.objects.get(id=self.note1.id)

        self.assertEqual(note.title, self.note1.title)
        self.assertEqual(note.text, self.note1.text)
        self.assertEqual(note.slug, self.note1.slug)
        self.assertEqual(note.author, self.note1.author)

    def test_user_cannot_delete_others_note(self):
        """
        Тестирует, что пользователь не может
        редактировать или удалять чужие заметки.
        """
        self.assertEqual(self.note1.author, self.user1)
        response = self.client_user2.post(DELETE_URL)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter
                        (id=self.note1.id).exists()
                        )

        note = Note.objects.get(id=self.note1.id)

        self.assertEqual(note.title, self.note1.title)
        self.assertEqual(note.text, self.note1.text)
        self.assertEqual(note.slug, self.note1.slug)
        self.assertEqual(note.author, self.note1.author)
