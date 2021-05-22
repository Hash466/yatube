from django.test import TestCase

from posts.models import Group, Post, User  # type: ignore


class ModelTest(TestCase):

    def test_str_post_group(self):
        """__str__ post / group - это начало текста поста / имя группы."""
        test_user = User.objects.create_user(username='test_model_user')
        post = Post.objects.create(text='Тестовый пост проверок моделей',
                                   author=test_user)
        group = Group.objects.create(title='Тестирование моделей',
                                     slug='test-models')

        objects_model = {
            post: post.text[:15],
            group: group.title
        }
        for object_model_str, object_model_slice in objects_model.items():
            with self.subTest(object_model=object_model_str):
                self.assertEqual(str(object_model_str), object_model_slice)
