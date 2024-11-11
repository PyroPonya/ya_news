import pytest

from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News

pytestmark = pytest.mark.django_db


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
    return Comment.objects.create(text='text', author=author, news=get_news)
