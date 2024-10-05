from http import HTTPStatus

from .base import (ADD_URL, DELETE_URL, DETAIL_URL, EDIT_URL, HOME_PAGE_URL,
                   LIST_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL, SUCCESS_URL,
                   BaseTestData)


class TestRoutes(BaseTestData):

    def test_pages_availability(self):
        """Доступность основных страниц для анонимных пользователей."""
        cases = [
            [HOME_PAGE_URL, self.client, HTTPStatus.OK],
            [LOGIN_URL, self.client, HTTPStatus.OK],
            [LOGOUT_URL, self.client, HTTPStatus.OK],
            [SIGNUP_URL, self.client, HTTPStatus.OK],

            [SUCCESS_URL, self.client_user1, HTTPStatus.OK],
            [ADD_URL, self.client_user1, HTTPStatus.OK],
            [LIST_URL, self.client_user1, HTTPStatus.OK],

            [EDIT_URL(self.note1.slug), self.client_user1, HTTPStatus.OK],
            [DELETE_URL(self.note1.slug), self.client_user1, HTTPStatus.OK],
            [DETAIL_URL(self.note1.slug), self.client_user1, HTTPStatus.OK],

            [EDIT_URL(self.note1.slug), self.client_user2,
             HTTPStatus.NOT_FOUND],
            [DELETE_URL(self.note1.slug), self.client_user2,
             HTTPStatus.NOT_FOUND],
            [DETAIL_URL(self.note1.slug), self.client_user2,
             HTTPStatus.NOT_FOUND]
        ]
        for url_name, client_instance, exp_status_code in cases:
            with self.subTest(name=url_name):
                response = client_instance.get(url_name)
                self.assertEqual(response.status_code, exp_status_code)

    def test_redirect_for_anonymous_client(self):
        """
        Проверяет, что анонимные пользователи
        перенаправляются на страницу входа.
        """
        urls = [LIST_URL, SUCCESS_URL, ADD_URL,
                DETAIL_URL(self.note1.slug), EDIT_URL(self.note1.slug),
                DELETE_URL(self.note1.slug)]
        for url_name in urls:
            with self.subTest(name=url_name):
                redirect_url = f'{LOGIN_URL}?next={url_name}'
                self.assertRedirects(self.client.get(url_name), redirect_url)
