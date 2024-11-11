import pytest

from django.urls import reverse

from news.forms import CommentForm


# Количество новостей на главной странице — не более 10.
@pytest.mark.django_db
def test_home_page_content(client, get_news):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context['object_list']) <= 10

# Новости отсортированы от самой свежей к самой старой. Свежие новости в начале списка.
@pytest.mark.django_db
def test_home_page_order(client, get_news):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['object_list'][0] == get_news

# Комментарии на странице отдельной новости отсортированы в хронологическом порядке: старые в начале списка, новые — в конце.
@pytest.mark.django_db
def test_detail_page_order(client, get_comment, get_news):
    url = reverse('news:detail', args=(get_news.id,))
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['news'].comment_set.all()[0] == get_comment

# Анонимному пользователю недоступна форма для отправки комментария на странице отдельной новости.
@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, get_news):
    url = reverse('news:detail', args=(get_news.id,))
    response = client.get(url)
    assert 'form' not in response.context

# Авторизованному пользователю доступна форма для отправки комментария на странице отдельной новости.
@pytest.mark.django_db
def test_author_client_has_form(author_client, get_news):
    url = reverse('news:detail', args=(get_news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
