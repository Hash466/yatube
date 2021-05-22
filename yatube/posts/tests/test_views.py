from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm  # type: ignore
from posts.models import Group, Post  # type: ignore
from yatube.settings import COUNT_POSTS  # type: ignore

User = get_user_model()


class PostsViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username='test_view_user')
        cls.group1 = Group.objects.create(title='Тестирование views',
                                          slug='test-views',
                                          description='Так - потестить!')
        cls.post = Post.objects.create(text='Тестовый пост проверок views',
                                       author=cls.test_user,
                                       group=cls.group1)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewTests.test_user)

    def check_post(self, context, is_post):
        if is_post:
            self.assertIn('post', context)
            object = context['post']
        else:
            self.assertIn('page', context)
            object = context['page'][0]

        self.assertEqual(object.text, PostsViewTests.post.text)
        self.assertEqual(object.author, PostsViewTests.test_user)
        self.assertEqual(object.group, PostsViewTests.group1)
        self.assertEqual(object.pub_date, PostsViewTests.post.pub_date)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        test_user = PostsViewTests.test_user.username
        post_id = PostsViewTests.post.id
        group_slug = PostsViewTests.group1.slug

        pages_names_templates = (
            ('index', None, 'posts/index.html'),
            ('group_posts', (group_slug,), 'posts/group.html'),
            ('new_post', None, 'posts/new_post.html'),
            ('profile', (test_user,), 'posts/profile.html'),
            ('post', (test_user, post_id,), 'posts/post.html'),
            ('post_edit', (test_user, post_id,), 'posts/new_post.html'),
        )

        for reverse_name, args, template in pages_names_templates:
            with self.subTest(template=template, reverse_name=reverse_name):
                response = self.authorized_client.get(reverse(reverse_name,
                                                              args=args))
                self.assertTemplateUsed(response, template)

    def test_pages_index_show_correct_context(self):
        """Шаблон posts/index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        self.check_post(response.context, is_post=False)

    def test_pages_group_show_correct_context(self):
        """Шаблон group.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': PostsViewTests.group1.slug})
        )
        self.assertIn('group', response.context)
        object_group = response.context['group']
        self.assertEqual(object_group.title, PostsViewTests.group1.title)
        self.assertEqual(object_group.description,
                         PostsViewTests.group1.description)
        self.check_post(response.context, is_post=False)

    def test_pages_group_show_no_posts(self):
        """В другой группе нет постов и group.html с правильным контекстом."""
        Post.objects.create(text='Тестовый пост show_no_posts',
                            author=PostsViewTests.test_user,
                            group=PostsViewTests.group1,)
        group2 = Group.objects.create(title='Тестирование views, group2',
                                      slug='test-group2-views',
                                      description='Иначе - потестить!')
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': group2.slug})
        )
        self.assertIn('group', response.context)
        self.assertEqual(len(response.context.get('page').object_list), 0)

    def test_pages_profile_show_correct_context(self):
        """Шаблон posts/profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'profile',
                kwargs={'username': PostsViewTests.test_user.username},
            )
        )
        self.check_post(response.context, is_post=False)
        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], PostsViewTests.test_user)

    def test_pages_post_view_show_correct_context(self):
        """Шаблон posts/post.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'post',
                kwargs={
                    'username': PostsViewTests.test_user.username,
                    'post_id': PostsViewTests.post.id,
                },
            )
        )
        self.check_post(response.context, is_post=True)
        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], PostsViewTests.test_user)

    def test_pages_display_the_correct_number_of_posts(self):
        """На страницах выводится верное количество постов."""
        objects_set = [
            Post(
                text=f"Тестовый пост № {item}",
                author=PostsViewTests.test_user,
                group=PostsViewTests.group1
            )
            for item in range(12)
        ]
        Post.objects.bulk_create(objects_set)
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list),
                         COUNT_POSTS)

    def test_pages_post_edit_show_correct_context(self):
        """Шаблон posts/new_post.html сформирован с правильным контекстом."""
        post = Post.objects.create(text='Тестовый пост проверок forms',
                                   author=PostsViewTests.test_user,
                                   group=PostsViewTests.group1)

        response_edit = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={
                        'username': post.author.username,
                        'post_id': post.id
                    }))
        self.assertIn('edit', response_edit.context)
        self.assertIs(response_edit.context['edit'], True)
        self.assertIn('form', response_edit.context)
        self.assertIsInstance(response_edit.context['form'], PostForm)

        response_new = self.authorized_client.get(reverse('new_post'))
        self.assertIn('edit', response_new.context)
        self.assertIs(response_new.context['edit'], False)
        self.assertIn('form', response_new.context)
        self.assertIsInstance(response_new.context['form'], PostForm)
