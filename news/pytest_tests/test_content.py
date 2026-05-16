# test_content.py
import pytest
from django.conf import settings
from django.urls import reverse
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


class TestHomePage:
    def test_news_count(self, client, home_url, bulk_news):
        response = client.get(home_url)
        object_list = response.context['object_list']
        assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_news_order(self, client, home_url, bulk_news):
        response = client.get(home_url)
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        assert all_dates == sorted_dates


class TestDetailPage:
    def test_comments_order(self, client, detail_news, bulk_comments):
        detail_url = reverse('news:detail', args=(detail_news.id,))
        response = client.get(detail_url)
        assert 'news' in response.context
        news = response.context['news']
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps

    def test_anonymous_client_has_no_form(self, client, detail_news):
        detail_url = reverse('news:detail', args=(detail_news.id,))
        response = client.get(detail_url)
        assert 'form' not in response.context

    def test_authorized_client_has_form(self, client, detail_author, detail_news):
        client.force_login(detail_author)
        detail_url = reverse('news:detail', args=(detail_news.id,))
        response = client.get(detail_url)
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
