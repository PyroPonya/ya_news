import pytest

from django.urls import reverse
from pytils.translit import slugify
from pytest_django.asserts import assertRedirects, assertFormError
from http import HTTPStatus

from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING


# Анонимный пользователь не может отправить комментарий.
@pytest.mark.django_db
def test_anonymous_user_cant_comment(client, get_news):
    url = reverse('news:detail', args=(get_news.id,))
    response = client.post(url, data={'text': 'Какой-то текст'})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0

# Авторизованный пользователь может отправить комментарий.
@pytest.mark.django_db
def test_user_can_comment(author_client, get_news):
    url = reverse('news:detail', args=(get_news.id,))
    response = author_client.post(url, data={'text': 'Какой-то текст'})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1

# Если комментарий содержит запрещённые слова, он не будет опубликован, а форма вернёт ошибку.
@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, get_news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(get_news.id,))
    response = author_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0

# Авторизованный пользователь может редактировать или удалять свои комментарии.
@pytest.mark.django_db
def test_user_can_edit_or_delete_comment(author_client, get_comment):
    url = reverse('news:edit', args=(get_comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 1

# Авторизованный пользователь не может редактировать или удалять чужие комментарии.
@pytest.mark.django_db
def test_user_cant_edit_or_delete_another_comment(reader_client, get_comment):
    url = reverse('news:edit', args=(get_comment.id,))
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
