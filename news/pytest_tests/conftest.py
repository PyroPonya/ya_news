from datetime import timedelta
from django.utils import timezone

import pytest
from django.test.client import Client
from django.urls import reverse


from news.models import Comment, News

import yanews.settings as settings


@pytest.fixture(autouse=True)
def allow_db(db):
    yield


"""Url fixtures start"""


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(get_news):
    return reverse('news:detail', args=(get_news.id,))


@pytest.fixture
def edit_url(get_comment):
    return reverse('news:edit', args=(get_comment.id,))


@pytest.fixture
def delete_url(get_comment):
    return reverse('news:delete', args=(get_comment.id,))


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


"""Url fixtures end"""


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create_user(username='author')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create_user(username='reader')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def get_news():
    return News.objects.create(title='title', text='text')


@pytest.fixture
def get_comment(author, get_news):
    return Comment.objects.create(
        text='Какой-то текст', author=author, news=get_news
    )


@pytest.fixture
def get_multiple_news():
    News.objects.bulk_create(
        [News(title=f'title {i}', text=f'text {i}', date=timezone.now(
        ) - timedelta(days=i)) for i in range(
            settings.NEWS_COUNT_ON_HOME_PAGE + 1
        )]
    )


@ pytest.fixture
def get_multiple_comments(author, get_news):
    for i in range(10):
        new_comment = Comment.objects.create(
            text=f'Какой-то текст {i}', author=author, news=get_news
        )
        new_comment.created = timezone.now() - timedelta(days=i)
        new_comment.save()
