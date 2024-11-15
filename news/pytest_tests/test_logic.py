from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


BASIC_COMMENT_DATA = {'text': 'Какой-то текст'}
BAD_COMMENT_DATA = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
NEW_COMMENT_DATA = {'text': 'Новый комментарий'}


def test_anonymous_user_cant_comment(
        client, detail_url, get_news
):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(detail_url, data=BASIC_COMMENT_DATA)
    assert Comment.objects.count() == 0


def test_user_can_comment(author_client, detail_url, get_news):
    """Авторизованный пользователь может отправить комментарий."""
    author_client.post(detail_url, data=BASIC_COMMENT_DATA)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == BASIC_COMMENT_DATA['text']
    assert comment.news == get_news
    assert comment.author == comment.author


def test_user_cant_use_bad_words(
        author_client, detail_url, get_news
):
    """Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    response = author_client.post(detail_url, data=BAD_COMMENT_DATA)
    assert Comment.objects.count() == 0
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )


def test_user_can_edit_comment(
        author_client, edit_url, get_comment
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = author_client.get(edit_url)
    assert response.status_code == HTTPStatus.OK
    response = author_client.post(edit_url, data=NEW_COMMENT_DATA)
    assertRedirects(response, f'/news/{get_comment.news.pk}/#comments')
    edited_comment = Comment.objects.get(id=get_comment.id)
    assert edited_comment.text == NEW_COMMENT_DATA['text']
    assert edited_comment.author == get_comment.author
    assert edited_comment.news == get_comment.news


def test_user_can_delete_comment(author_client, delete_url, get_comment):
    """Авторизованный пользователь может  свои комментарии."""
    response = author_client.post(delete_url)
    assertRedirects(response, f'/news/{get_comment.news.pk}/#comments')
    assert Comment.objects.count() == 0


def test_user_cant_edit_another_comment(
        edit_url, reader_client, get_comment
):
    """Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    response = reader_client.post(edit_url, data=NEW_COMMENT_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment = Comment.objects.get(id=get_comment.id)
    assert comment.text == get_comment.text
    assert comment.author == get_comment.author
    assert comment.news == get_comment.news


def test_user_cant_delete_another_comment(
        delete_url, reader_client, get_comment
):
    """Авторизованный пользователь не может удалить
    чужие комментарии.
    """
    response = reader_client.get(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
