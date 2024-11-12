import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects

from news.models import Comment
from news.forms import BAD_WORDS


BASIC_COMMENT_DATA = {'text': 'Какой-то текст'}
BAD_COMMENT_DATA = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
NEW_COMMENT_DATA = {'text': 'Новый комментарий'}


def test_anonymous_user_cant_comment(
    build_url, client, get_news
):
    """Анонимный пользователь не может отправить комментарий."""
    url = build_url('news:detail', get_news.id)
    client.post(url, data=BASIC_COMMENT_DATA)
    assert Comment.objects.count() == 0


def test_user_can_comment(author_client, build_url, get_news):
    """Авторизованный пользователь может отправить комментарий."""
    url = build_url('news:detail', get_news.id)
    author_client.post(url, data=BASIC_COMMENT_DATA)
    assert Comment.objects.count() == 1


def test_user_cant_use_bad_words(
    author_client, build_url, get_news
):
    """Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = BAD_COMMENT_DATA
    url = build_url('news:detail', get_news.id)
    author_client.post(url, data=bad_words_data)
    assert Comment.objects.count() == 0


def test_user_can_edit_comment(
    author_client, build_url, get_comment
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    url = build_url('news:edit', get_comment.id)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 1
    response = author_client.post(url, data=NEW_COMMENT_DATA)
    assertRedirects(response, f'/news/{get_comment.news.pk}/#comments')
    assert Comment.objects.count() == 1
    get_comment.refresh_from_db()
    assert get_comment.text == NEW_COMMENT_DATA['text']


def test_user_can_delete_comment(author_client, build_url, get_comment):
    """Авторизованный пользователь может  свои комментарии."""
    url = build_url('news:delete', get_comment.id)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 1
    response = author_client.post(url)
    assertRedirects(response, f'/news/{get_comment.news.pk}/#comments')
    assert Comment.objects.count() == 0


def test_user_cant_edit_or_delete_another_comment(
    build_url, reader_client, get_comment
):
    """Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    url = build_url('news:edit', get_comment.id)
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    reader_client.post(url, data=NEW_COMMENT_DATA)
    get_comment.refresh_from_db()
    assert get_comment.text == BASIC_COMMENT_DATA['text']


def test_user_cant_delete_another_comment(
    build_url, reader_client, get_comment
):
    """Авторизованный пользователь не может удалить
    чужие комментарии.
    """
    url = build_url('news:delete', get_comment.id)
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    reader_client.post(url)
    assert Comment.objects.count() == 1
