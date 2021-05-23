import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post  # type: ignore

User = get_user_model()


SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст поста из формы',
            'group': PostCreateFormTests.group.id,
            'image': uploaded,
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
        self.assertEqual(post.image.name, 'posts/small.gif')

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

    def test_guest_cannot_comment(self):
        """Форма не позволяет гостю оставлять комментарии к постам."""
        author = PostCreateFormTests.test_user
        post = Post.objects.create(text='Тестовый пост проверок forms',
                                   author=author)
        Comment.objects.create(post=post, author=author,
                               text='абракатабра хе-хе')
        comment_count = post.comments.count()
        form_data = {'text': 'Я аноним, комментом гоним!'}
        self.client.post(reverse('add_comment',
                                 kwargs={
                                     'username': author,
                                     'post_id': post.id
                                 }), data=form_data)
        self.assertEqual(comment_count, post.comments.count())

    def test_user_can_comment(self):
        """Форма позволяет пользователю оставлять комментарии к постам."""
        author = PostCreateFormTests.test_user
        post = Post.objects.create(text='Тестовый пост для комментариев',
                                   author=author)
        comment_count = post.comments.count()
        form_data = {'text': 'Я НЕ аноним!'}
        response = self.authorized_client.post(reverse('add_comment',
                                                       kwargs={
                                                           'username': author,
                                                           'post_id': post.id
                                                       }), data=form_data)
        self.assertEqual(post.comments.count(), comment_count + 1)

        comm_obj = post.comments.all()[0]
        self.assertEqual(comm_obj.text, form_data['text'])
        self.assertEqual(comm_obj.author, author)
        self.assertRedirects(response, reverse('post',
                                               kwargs={
                                                   'username': author,
                                                   'post_id': post.id
                                               }))
