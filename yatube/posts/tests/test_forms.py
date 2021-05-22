from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post  # type: ignore

User = get_user_model()


class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username='test_view_user')
        cls.group = Group.objects.create(title='Тестирование forms',
                                         slug='test-forms',
                                         description='Потестить форму!')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.test_user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст поста из формы',
            'group': PostCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.first()
        self.assertEqual(post.group, PostCreateFormTests.group)
        self.assertEqual(post.author, PostCreateFormTests.test_user)
        self.assertEqual(post.text, form_data['text'])

    def test_edit_post(self):
        """Валидная форма редактирует запись поста."""
        group2 = Group.objects.create(title='Тестирование forms 2',
                                      slug='test-forms2',
                                      description='Потестить форму 2!')
        post = Post.objects.create(text='Тестовый пост проверок forms',
                                        author=PostCreateFormTests.test_user,
                                        group=PostCreateFormTests.group)
        posts_count = Post.objects.count()
        form_data = {
            'group': group2.id,
            'text': 'Отредактированный тестовый текст поста из формы',
        }
        self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': PostCreateFormTests.test_user,
                    'post_id': post.id,
                },
            ),
            data=form_data,
            follow=True
        )
        object_post = Post.objects.get(id=post.id)
        self.assertEqual(object_post.text, form_data['text'])
        self.assertEqual(object_post.group, group2)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(object_post.author, PostCreateFormTests.test_user)

    def test_error_creating_guest_user(self):
        """Форма не позволяет создавать новый пост анониму."""
        form_data = {'text': 'Я аноним!'}
        posts_count = Post.objects.count()
        response = self.client.post(reverse('new_post'), data=form_data)
        self.assertEqual(posts_count, Post.objects.count())
        self.assertRedirects(
            response, (reverse('login') + '?next=' + reverse('new_post'))
        )

    def test_error_editing_not_author(self):
        """Форма не позволяет редактировать запись другому пользователю."""
        post = Post.objects.create(text='Тестовый пост проверок forms',
                                   author=PostCreateFormTests.test_user)
        post_count = Post.objects.count()
        test_author = User.objects.create_user(username='test_author')
        self.reader_client = Client()
        self.reader_client.force_login(test_author)

        form_data = {'text': 'Я аноним!', 'group': PostCreateFormTests.group}

        kwargs_reverse = {
            'username': PostCreateFormTests.test_user, 'post_id': post.id
        }
        response = self.reader_client.post(
            reverse('post_edit', kwargs=kwargs_reverse), data=form_data
        )
        post_latest = Post.objects.get(id=post.id)
        self.assertNotEqual(post_latest.text, form_data['text'])
        self.assertNotEqual(post_latest.group, PostCreateFormTests.group)
        self.assertNotEqual(post_latest.author, test_author)
        self.assertEqual(post_count, Post.objects.count())
        self.assertRedirects(response, reverse('post', kwargs=kwargs_reverse))
