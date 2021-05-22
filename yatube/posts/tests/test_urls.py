from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User  # type: ignore


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='test_author')
        cls.group = Group.objects.create(title='Тестирование url-ов',
                                         slug='test-urls')
        cls.post = Post.objects.create(text='Тестовый пост проверок url-ов',
                                       author=PostsURLTests.user_author,
                                       group=PostsURLTests.group)

    def setUp(self):
        self.client_author = Client()
        self.client_author.force_login(PostsURLTests.user_author)

    def test_urls(self):
        """Корректный URL-адрес."""
        group_slup = PostsURLTests.group.slug
        post_id = PostsURLTests.post.id
        username = PostsURLTests.user_author.username

        paths_url_reverse = (
            ('/', 'index', None),
            (f'/group/{group_slup}/', 'group_posts', (group_slup,)),
            (f'/{username}/', 'profile', (username,)),
            (f'/{username}/{post_id}/', 'post', (username, post_id)),
            ('/new/', 'new_post', None),
            (f'/{username}/{post_id}/edit/', 'post_edit',
             (username, post_id)),
        )

        for absol_addr, name, rev_args in paths_url_reverse:
            with self.subTest(absolute_address=absol_addr,
                              reverse_name=name):
                self.assertEqual(absol_addr, reverse(name, args=rev_args))

    def test_urls_access(self):
        """Ожидаемый доступ к URL-адресу."""
        group_slup = PostsURLTests.group.slug
        post_id = PostsURLTests.post.id
        username_author = PostsURLTests.user_author.username

        path_client = (
            ('/', self.client),
            (f'/group/{group_slup}/', self.client),
            (f'/{username_author}/{post_id}/', self.client),
            ('/new/', self.client_author),
            (f'/{username_author}/{post_id}/edit/', self.client_author),
        )

        for url, client_type in path_client:
            with self.subTest(url=url, client_type=client_type):
                response = client_type.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirects(self):
        """Ожидаемый редирект при доступе к URL-адресу."""
        post_id = PostsURLTests.post.id
        username = PostsURLTests.user_author.username
        user_reader = User.objects.create_user(username='test_readr')
        user_client = Client()
        user_client.force_login(user_reader)
        guest_client = self.client

        urls_clients_redirects = (
            ('new_post', None, guest_client,
             (reverse('login') + '?next=' + reverse('new_post'))),
            ('post_edit', (username, post_id), user_client,
             reverse('post', args=(username, post_id))),
            ('post_edit', (username, post_id), guest_client,
             (reverse('login') + '?next=' + reverse('post_edit',
                                                    args=(username, post_id)))
             ),
            ('add_comment', (username, post_id), guest_client,
             (reverse('login') + '?next=' + reverse('add_comment',
                                                    args=(username, post_id)))
             ),
        )

        for (get_name, rev_args, client_obj,
             redirect_url) in urls_clients_redirects:
            with self.subTest():
                response = client_obj.get(reverse(get_name, args=rev_args))
                self.assertRedirects(response, redirect_url)

    def test_http_status_404(self):
        """Ожидаемая ошибка 404 при запросе несуществующего URL."""
        response = self.client.get('/7у6еа7у6еа76у7к6а/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
