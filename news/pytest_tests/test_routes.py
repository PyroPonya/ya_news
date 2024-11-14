import pytest
from pytest_django.asserts import assertRedirects
from http import HTTPStatus


"""
Тесты на pytest для проекта YaNews.
В файле test_routes.py:
Главная страница доступна анонимному пользователю.
Страницы регистрации пользователей,
входа в учётную запись
и выхода из неё доступны анонимным пользователям.
Страница отдельной новости доступна анонимному пользователю.
Страницы удаления и редактирования комментария доступны
автору комментария.
При попытке перейти на страницу редактирования или удаления
комментария анонимный пользователь перенаправляется
на страницу авторизации.
Авторизованный пользователь не может зайти на страницы
редактирования или удаления чужих комментариев (возвращается ошибка 404).
"""


@ pytest.mark.parametrize(
    'url, user_client, status',
    (
        (pytest.lazy_fixture('home_url'),
         pytest.lazy_fixture('client'),
         HTTPStatus.OK
         ),
        (pytest.lazy_fixture('detail_url'),
         pytest.lazy_fixture('client'),
         HTTPStatus.OK
         ),
        (pytest.lazy_fixture('signup_url'),
         pytest.lazy_fixture('client'),
         HTTPStatus.OK
         ),
        (pytest.lazy_fixture('login_url'),
         pytest.lazy_fixture('client'),
         HTTPStatus.OK
         ),
        (pytest.lazy_fixture('logout_url'),
         pytest.lazy_fixture('client'),
         HTTPStatus.OK
         ),
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('author_client'),
         HTTPStatus.OK
         ),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('author_client'),
         HTTPStatus.OK
         ),
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('reader_client'),
         HTTPStatus.NOT_FOUND
         ),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('reader_client'),
         HTTPStatus.NOT_FOUND
         ),
    )
)
def test_detail_edit_delete_page_access_restricted_to_author(
    url, user_client, status, get_news, get_comment
):
    """
    Главная страница доступна анонимному пользователю.
    Страница отдельной новости доступна анонимному пользователю.
    Страницы регистрации пользователей, входа в учётную запись
    и выхода из неё доступны анонимным пользователям.
    Страницы удаления и редактирования комментария доступны автору комментария.
    Авторизованный пользователь не может зайти на страницы
    редактирования или удаления чужих комментариев (возвращается ошибка 404).
    """
    response = user_client.get(url)
    assert response.status_code == status


@ pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url'),
    )
)
def test_redirect_for_anonymous_edit_and_delete(
    client, get_comment, url
):
    response = client.get(url)
    assertRedirects(
        response, f'/auth/login/?next={url}')
