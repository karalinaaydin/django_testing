from http import HTTPStatus

from .base import (ADD_URL, DELETE_URL, DETAIL_URL, EDIT_URL, HOME_PAGE_URL,
                   LIST_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL, SUCCESS_URL,
                   BaseTestData, get_redirect_url)


class TestRoutes(BaseTestData):

    def test_pages_availability(self):
        """Доступность основных страниц для разных пользователей."""
        cases = [
            [HOME_PAGE_URL, self.client, HTTPStatus.OK],
            [LOGIN_URL, self.client, HTTPStatus.OK],
            [LOGOUT_URL, self.client, HTTPStatus.OK],
            [SIGNUP_URL, self.client, HTTPStatus.OK],

            [SUCCESS_URL, self.client_user1, HTTPStatus.OK],
            [ADD_URL, self.client_user1, HTTPStatus.OK],
            [LIST_URL, self.client_user1, HTTPStatus.OK],

            [EDIT_URL, self.client_user1, HTTPStatus.OK],
            [DELETE_URL, self.client_user1, HTTPStatus.OK],
            [DETAIL_URL, self.client_user1, HTTPStatus.OK],

            [EDIT_URL, self.client_user2, HTTPStatus.NOT_FOUND],
            [DELETE_URL, self.client_user2, HTTPStatus.NOT_FOUND],
            [DETAIL_URL, self.client_user2, HTTPStatus.NOT_FOUND],

            [SUCCESS_URL, self.client, HTTPStatus.FOUND],
            [ADD_URL, self.client, HTTPStatus.FOUND],
            [LIST_URL, self.client, HTTPStatus.FOUND],
            [EDIT_URL, self.client, HTTPStatus.FOUND],
            [DELETE_URL, self.client, HTTPStatus.FOUND],
            [DETAIL_URL, self.client, HTTPStatus.FOUND]
        ]
        for url, client_instance, exp_status_code in cases:
            with self.subTest(url=url, expected_status_code=exp_status_code):
                response = client_instance.get(url)
                self.assertEqual(response.status_code, exp_status_code)

    def test_redirect_for_anonymous_client(self):
        """
        Проверяет, что анонимные пользователи
        перенаправляются на страницу входа.
        """
        urls = [LIST_URL, SUCCESS_URL, ADD_URL,
                DETAIL_URL, EDIT_URL, DELETE_URL]
        for url in urls:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url),
                                     get_redirect_url(url))
