from django.db import models
from django.contrib.auth import get_user_model

from yatube.settings import POST_SYMBOLS, COMMENT_SYMBOLS
from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=200, blank=True)

    class Meta:
        ordering = ['title', ]

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Добавьте текст новой записи'
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True, null=True,
        verbose_name='Группа',
        help_text='Выберите группу для новой записи',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:POST_SYMBOLS]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        related_name='comment',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='comment',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Прокомментировать'
    )

    class Meta:
        ordering = ['-pub_date', ]

    def __str__(self):
        return self.text[:COMMENT_SYMBOLS]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = 'Подписки'
        verbose_name = 'Подписка'

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
