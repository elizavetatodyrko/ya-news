# test_logic.py
import pytest
from http import HTTPStatus
from django.urls import reverse
from news.models import Comment
from news.forms import BAD_WORDS, WARNING

pytestmark = pytest.mark.django_db


class TestCommentCreation:
    def test_anonymous_user_cant_create_comment(self, client, news, form_data):
        url = reverse('news:detail', args=(news.id,))
        client.post(url, data=form_data)
        assert Comment.objects.count() == 0

    def test_user_can_create_comment(self, author_client, author, news, form_data):
        url = reverse('news:detail', args=(news.id,))
        response = author_client.post(url, data=form_data)
        expected_url = f'{url}#comments'
        assert response.status_code == HTTPStatus.FOUND
        assert response['Location'] == expected_url
        assert Comment.objects.count() == 1
        comment = Comment.objects.get()
        assert comment.text == form_data['text']
        assert comment.news == news
        assert comment.author == author

    def test_user_cant_use_bad_words(self, author_client, news):
        url = reverse('news:detail', args=(news.id,))
        bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
        response = author_client.post(url, data=bad_words_data)
        form = response.context['form']
        assert form.errors['text'] == [WARNING]
        assert Comment.objects.count() == 0


class TestCommentEditDelete:
    def test_author_can_delete_comment(self, author_client, comment, detail_url):
        delete_url = reverse('news:delete', args=(comment.id,))
        response = author_client.delete(delete_url)
        expected_url = f'{detail_url}#comments'
        assert response.status_code == HTTPStatus.FOUND
        assert response['Location'] == expected_url
        assert Comment.objects.count() == 0

    def test_user_cant_delete_comment_of_another_user(self, reader_client, comment):
        delete_url = reverse('news:delete', args=(comment.id,))
        response = reader_client.delete(delete_url)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Comment.objects.count() == 1

    def test_author_can_edit_comment(self, author_client, comment, detail_url):
        edit_url = reverse('news:edit', args=(comment.id,))
        new_text = 'Обновлённый комментарий'
        form_data = {'text': new_text}
        response = author_client.post(edit_url, data=form_data)
        expected_url = f'{detail_url}#comments'
        assert response.status_code == HTTPStatus.FOUND
        assert response['Location'] == expected_url
        comment.refresh_from_db()
        assert comment.text == new_text

    def test_user_cant_edit_comment_of_another_user(self, reader_client, comment):
        edit_url = reverse('news:edit', args=(comment.id,))
        new_text = 'Обновлённый комментарий'
        form_data = {'text': new_text}
        response = reader_client.post(edit_url, data=form_data)
        assert response.status_code == HTTPStatus.NOT_FOUND
        comment.refresh_from_db()
        assert comment.text == 'Текст комментария'  # исходный текст
