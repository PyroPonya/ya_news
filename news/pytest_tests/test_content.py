from http import HTTPStatus

from news.forms import CommentForm
import yanews.settings as settings


def test_home_page_content(
        client, get_multiple_news, home_url
):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK
    assert 'object_list' in response.context
    all_news = response.context['object_list']
    news_count = all_news.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_home_page_order(
        client, get_multiple_news, home_url
):
    """Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK
    assert 'object_list' in response.context
    all_news = response.context['object_list']
    all_dates = [news.date for news in all_news]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_detail_page_order(
        client, detail_url, get_multiple_comments, get_news
):
    """Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK
    all_comments = get_news.comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


def test_anonymous_client_has_no_form(
        client, detail_url, get_news
):
    """Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости.
    """
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_author_client_has_form(
        author_client, detail_url, get_news
):
    """Авторизованному пользователю доступна форма для отправки
    комментария на странице отдельной новости.
    """
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
