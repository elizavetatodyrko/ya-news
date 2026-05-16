# test_routes.py
import pytest
from http import HTTPStatus
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestRoutes:
    @pytest.mark.parametrize(
        'url_name, args',
        [
            ('news:home', None),
            ('news:detail', lambda news: (news.id,)),
            ('users:login', None),
            ('users:signup', None),
        ],
        ids=['home', 'detail', 'login', 'signup']
    )
    def test_pages_availability(self, client, news, url_name, args):
        if callable(args):
            args = args(news)
        url = reverse(url_name, args=args) if args else reverse(url_name)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize(
        'user_fixture, expected_status',
        [
            ('author_client', HTTPStatus.OK),
            ('reader_client', HTTPStatus.NOT_FOUND),
        ],
        ids=['author', 'reader']
    )
    @pytest.mark.parametrize(
        'url_name',
        ['news:edit', 'news:delete'],
        ids=['edit', 'delete']
    )
    def test_availability_for_comment_edit_and_delete(
        self, request, comment, url_name, user_fixture, expected_status
    ):
        client = request.getfixturevalue(user_fixture)
        url = reverse(url_name, args=(comment.id,))
        response = client.get(url)
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        'url_name',
        ['news:edit', 'news:delete'],
        ids=['edit', 'delete']
    )
    def test_redirect_for_anonymous_client(self, client, comment, login_url, url_name):
        url = reverse(url_name, args=(comment.id,))
        redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response['Location'] == redirect_url
