from notes.forms import NoteForm

from .base import ADD_URL, edit_url, LIST_URL, BaseTestData


class TestContent(BaseTestData):

    def test_note_in_object_list(self):
        """
        Тестирует, что заметка отображается на странице
        списка заметок в object_list.
        """
        response = self.client_user1.get(LIST_URL)
        self.assertIn(self.note1, response.context['object_list'])
        note_from_context = (response.context['object_list']
                             .filter(slug=self.note1.slug).first())

        self.assertEqual(note_from_context.title, self.note1.title)
        self.assertEqual(note_from_context.text, self.note1.text)
        self.assertEqual(note_from_context.author, self.note1.author)

    def test_user_notes_dont_include_other_users_notes(self):
        """
        Тестирует, что в списке заметок пользователя
        не отображаются заметки других пользователей.
        """
        response = self.client_user1.get(LIST_URL)
        self.assertNotIn(self.note2, response.context['object_list'])

    def test_creation_page_contains_form(self):
        """
        Тестирует, что на страницах создания и редактирования заметки
        передаются формы.
        """
        urls = [ADD_URL, edit_url(self.note1.slug)]
        for url_name in urls:
            with self.subTest(name=url_name):
                response = self.client_user1.get(url_name)
                self.assertIn('form', response.context)

                form = response.context['form']
                self.assertIsInstance(form, NoteForm)
