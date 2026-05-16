import pytest
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING

User = get_user_model()


@pytest.fixture
def author(db):
    return User.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(db):
    return User.objects.create(username='Читатель простой')


@pytest.fixture
def news(db):
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def comment(db, author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def form_data():
    return {'text': 'Текст комментария'}


# Фикстуры для тестирования главной страницы (много новостей)
@pytest.fixture
def bulk_news(db):
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return News.objects.all()


# Фикстуры для детальной страницы (комментарии)
@pytest.fixture
def detail_news(db):
    return News.objects.create(title='Тестовая новость', text='Просто текст.')


@pytest.fixture
def detail_author(db):
    return User.objects.create(username='Комментатор')


@pytest.fixture
def bulk_comments(db, detail_news, detail_author):
    now = timezone.now()
    comments = []
    for index in range(10):
        comment = Comment.objects.create(
            news=detail_news,
            author=detail_author,
            text=f'Текст {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments
