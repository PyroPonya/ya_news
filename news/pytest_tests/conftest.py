from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.urls import reverse


from news.models import Comment, News


@pytest.fixture(autouse=True)
def allow_db(db):
    yield


@pytest.fixture()
def build_url():
    def _build_url(name, *args):
        if None in args:
            return reverse(name)
        return reverse(name, args=args)

    return _build_url


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
        [News(title=f'title {i}', text=f'text {i}', date=datetime.today(
        ) - timedelta(days=i)) for i in range(20)]
    )
    return News.objects.all()


@ pytest.fixture
def get_multiple_comments(author, get_news):
    Comment.objects.bulk_create(
        [
            Comment(text=f'text {i}', author=author, news=get_news,
                    created=datetime.today() - timedelta(days=i))
            for i in range(20)
        ]
    )
    return Comment.objects.all()
