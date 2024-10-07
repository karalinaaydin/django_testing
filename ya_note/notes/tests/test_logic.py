from http import HTTPStatus

from pytils.translit import slugify as pytils_slugify

from notes.models import Note
from .base import (ADD_URL, DELETE_URL, EDIT_URL, BaseTestData,
                   get_redirect_url)


class TestNoteLogic(BaseTestData):

    def test_logged_in_user_can_create_note(self):
        """Тестирует, что залогиненный пользователь может создать заметку."""
        Note.objects.all().delete()
        response = self.client_user1.post(ADD_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        created_note = Note.objects.get(author=self.user1,
                                        title=self.form_data['title'],
                                        text=self.form_data['text'],
                                        slug=self.form_data['slug'])

        self.assertEqual(Note.objects.filter(id=created_note.id).count(), 1)

    def test_anonymous_user_cannot_create_note(self):
        """Тестирует, что анонимный пользователь не может создать заметку."""
        note_count_before = Note.objects.count()
        response = self.client_anonymous.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, get_redirect_url(ADD_URL))
        note_count_after = Note.objects.count()
        self.assertEqual(note_count_before, note_count_after)

    def test_cannot_create_two_notes_with_same_slug(self):
        """Тестирует, что нельзя создать две заметки с одинаковым slug."""
        note_count_before = Note.objects.count()
        self.form_data['slug'] = self.note1.slug
        self.client_user1.post(ADD_URL, data=self.form_data)
        note_count_after = Note.objects.count()
        self.assertEqual(note_count_before, note_count_after)

    def test_slug_is_generated_if_not_provided(self):
        """
        Тестирует, что slug генерируется автоматически,
        если его не заполнить.
        """
        self.form_data['slug'] = ''
        response = self.client_user1.post(ADD_URL, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        note = note = Note.objects.latest('id')
        expected_slug = pytils_slugify(self.form_data['title'])

        self.assertEqual(note.slug, expected_slug)
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user1)

    def test_user_can_edit_own_note(self):
        """
        Тестирует, что пользователь может
        редактировать и удалять свои заметки.
        """
        original_author = self.note1.author
        self.client_user1.post(EDIT_URL,
                               data=self.form_data)
        edited_note = Note.objects.get(pk=self.note1.pk)
        self.assertEqual(edited_note.author, original_author)

        self.assertEqual(edited_note.title, self.form_data['title'])
        self.assertEqual(edited_note.text, self.form_data['text'])
        self.assertEqual(edited_note.slug, self.form_data['slug'])

    def test_user_can_delete_own_note(self):
        """
        Тестирует, что пользователь может
        редактировать и удалять свои заметки.
        """
        initial_count = Note.objects.count()

        self.client_user1.post(DELETE_URL)
        self.assertFalse(Note.objects.filter
                         (id=self.note1.id).exists()
                         )
        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_user_cannot_edit_others_note(self):
        """
        Тестирует, что пользователь не может
        редактировать или удалять чужие заметки.
        """
        original_title = self.note1.title
        original_text = self.note1.text
        original_slug = self.note1.slug
        original_author = self.note1.author

        response = self.client_user2.post(EDIT_URL, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.assertEqual(self.note1.title, original_title)
        self.assertEqual(self.note1.text, original_text)
        self.assertEqual(self.note1.slug, original_slug)
        self.assertEqual(self.note1.author, original_author)

    def test_user_cannot_delete_others_note(self):
        """
        Тестирует, что пользователь не может
        редактировать или удалять чужие заметки.
        """
        original_title = self.note1.title
        original_text = self.note1.text
        original_slug = self.note1.slug
        original_author = self.note1.author

        self.assertEqual(self.note1.author, self.user1)

        response = self.client_user2.post(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter
                        (id=self.note1.id).exists()
                        )

        note_after_attempt = Note.objects.get(id=self.note1.id)
        self.assertEqual(note_after_attempt.title, original_title)
        self.assertEqual(note_after_attempt.text, original_text)
        self.assertEqual(note_after_attempt.slug, original_slug)
        self.assertEqual(note_after_attempt.author, original_author)
