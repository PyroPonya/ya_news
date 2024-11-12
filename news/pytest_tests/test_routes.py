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


@pytest.mark.parametrize(
    'url, args',
    (
        ('news:home', False),
        ('news:detail', True),
        ('users:signup', False),
        ('users:login', False),
        ('users:logout', False),
    )
)
def test_auth_pages_anonymous_user(args, build_url, client, url, get_news):
    """
    Главная страница доступна анонимному пользователю.
    Страница отдельной новости доступна анонимному пользователю.
    Страницы регистрации пользователей, входа в учётную запись
    и выхода из неё доступны анонимным пользователям.
    """
    if not args:
        response = client.get(build_url(url))
    else:
        response = client.get(build_url(url, get_news.id))
    assert response.status_code == HTTPStatus.OK


@ pytest.mark.parametrize(
    'url, user_client, status',
    (
        ('news:edit', (
            pytest.lazy_fixture('author_client')
        ), HTTPStatus.OK),
        ('news:delete', (
            pytest.lazy_fixture('author_client')
        ), HTTPStatus.OK),
        ('news:edit', (
            pytest.lazy_fixture('reader_client')
        ), HTTPStatus.NOT_FOUND),
        ('news:delete', (
            pytest.lazy_fixture('reader_client')
        ), HTTPStatus.NOT_FOUND),
    )
)
def test_detail_edit_delete_page_access_restricted_to_author(
    build_url, url, user_client, status, get_news, get_comment
):
    """
    Страницы удаления и редактирования комментария доступны автору комментария.
    Авторизованный пользователь не может зайти на страницы
    редактирования или удаления чужих комментариев (возвращается ошибка 404).
    """
    response = user_client.get(build_url(url, get_comment.id))
    assert response.status_code == status


@ pytest.mark.parametrize(
    'url',
    (
        'news:edit',
        'news:delete',
    )
)
def test_redirect_for_anonymous_edit_and_delete(
    build_url, client, get_comment, url
):
    response = client.get(build_url(url, get_comment.id))
    assertRedirects(
        response, f'/auth/login/?next={build_url(url, get_comment.id)}')
