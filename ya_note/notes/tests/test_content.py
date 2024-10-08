from notes.forms import NoteForm
from notes.models import Note

from .base import ADD_URL, EDIT_URL, LIST_URL, BaseTestData


class TestContent(BaseTestData):

    def test_note_in_object_list(self):
        """
        Тестирует, что заметка отображается на странице
        списка заметок в object_list.
        """
        self.assertTrue(Note.objects.filter(id=self.note1.id).exists())

        note = (self.client_user1
                .get(LIST_URL)
                .context['object_list']
                .get(id=self.note1.id))

        self.assertEqual(note.title, self.note1.title)
        self.assertEqual(note.text, self.note1.text)
        self.assertEqual(note.author, self.note1.author)
        self.assertEqual(note.slug, self.note1.slug)

    def test_user_notes_dont_include_other_users_notes(self):
        """
        Тестирует, что в списке заметок пользователя
        не отображаются заметки других пользователей.
        """
        self.assertNotIn(self.note1,
                         self.client_user2
                         .get(LIST_URL)
                         .context['object_list'])

    def test_creation_page_contains_form(self):
        """
        Тестирует, что на страницах создания и редактирования заметки
        передаются формы.
        """
        urls = [ADD_URL, EDIT_URL]
        for url in urls:
            with self.subTest(url=url):
                response = self.client_user1.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
