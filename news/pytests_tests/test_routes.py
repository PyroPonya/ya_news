import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.models import News, Comment


# Главная страница доступна анонимному пользователю.
@pytest.mark.django_db
def test_home_page_anonymous_user(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

# Страница отдельной новости доступна анонимному пользователю.
@pytest.mark.django_db
def test_detail_page_anonymous_user(client, get_news):
    news = get_news
    url = reverse('news:detail', args=(1,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

# Страницы удаления и редактирования комментария доступны автору комментария.
@pytest.mark.django_db
def test_edit_delete_page_author(author_client, get_comment):
    url = reverse('news:edit', args=(get_comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK

# При попытке перейти на страницу редактирования или удаления комментария анонимный пользователь перенаправляется на страницу авторизации.
@pytest.mark.django_db
@pytest.mark.parametrize('url', ('news:edit', 'news:delete'))
def test_edit_delete_page_anonymous_user(client, get_comment, url):
    construct_url = reverse(url, args=(get_comment.id,))
    response = client.get(construct_url)
    redirect_url = f'/auth/login/?next={construct_url}'
    assertRedirects(response, redirect_url)

# Авторизованный пользователь не может зайти на страницы редактирования или удаления чужих комментариев (возвращается ошибка 404).
@pytest.mark.django_db
@pytest.mark.parametrize('url', ('news:edit', 'news:delete'))
def test_edit_delete_page_anonymous_user(reader_client, get_comment, url):
    construct_url = reverse(url, args=(get_comment.id,))
    response = reader_client.get(construct_url)
    assert response.status_code == HTTPStatus.NOT_FOUND

# Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны анонимным пользователям.
@pytest.mark.django_db
@pytest.mark.parametrize('url', ('users:signup', 'users:login', 'users:logout'))
def test_auth_pages_anonymous_user(client, url):
    construct_url = reverse(url)
    response = client.get(construct_url)
    assert response.status_code == HTTPStatus.OK
