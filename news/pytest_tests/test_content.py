import pytest

from news.forms import CommentForm


@pytest.mark.django_db
def test_home_page_content(
    build_url, client, get_multiple_news
):
    """Количество новостей на главной странице — не более 10."""
    url = build_url('news:home')
    response = client.get(url)
    assert response.status_code == 200
    all_news = response.context['object_list']
    news_count = all_news.count()
    assert news_count == 10


@pytest.mark.django_db
def test_home_page_order(
    build_url, client, get_multiple_news
):
    """Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    url = build_url('news:home')
    response = client.get(url)
    assert response.status_code == 200
    all_news = response.context['object_list']
    all_dates = [news.date for news in all_news]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_detail_page_order(
    build_url, client, get_multiple_comments, get_news
):
    """Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    url = build_url('news:detail', get_news.id)
    response = client.get(url)
    assert response.status_code == 200
    all_comments = get_news.comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_anonymous_client_has_no_form(
    build_url, client, get_news
):
    """Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости.
    """
    url = build_url('news:detail', get_news.id)
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_author_client_has_form(
    author_client, build_url, get_news
):
    """Авторизованному пользователю доступна форма для отправки
    комментария на странице отдельной новости.
    """
    url = build_url('news:detail', get_news.id)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
