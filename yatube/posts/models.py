from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name="Название группы",
                             max_length=200, unique=True)
    slug = models.SlugField(verbose_name="Уникальная часть URL",
                            unique=True)
    description = models.TextField(verbose_name="Описание",
                                   blank=True, null=True)

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Текст поста")
    pub_date = models.DateTimeField(verbose_name="Дата публикации",
                                    auto_now_add=True)
    author = models.ForeignKey(User, verbose_name="Автор поста",
                               on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True,
                              null=True, related_name="posts",
                              verbose_name="Группа")
    image = models.ImageField(upload_to='posts/', blank=True, null=True,
                              verbose_name="Картинка")

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments", verbose_name="Пост")
    text = models.TextField(verbose_name="Текст комментария")
    created = models.DateTimeField(verbose_name="Время публикации комментария",
                                   auto_now_add=True)
    author = models.ForeignKey(User, verbose_name="Автор комментария",
                               on_delete=models.CASCADE,
                               related_name="comments")

    class Meta:
        ordering = ("created",)
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"Комментарий от {self.author}: {self.text[:30]}"


class Follow(models.Model):
    user = models.ForeignKey(User, verbose_name="Подписчик",
                             on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, verbose_name="Автор",
                               on_delete=models.CASCADE,
                               related_name="following")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"
