"""Модели приложения users."""
from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_EMAIL_LENGTH = 254
MAX_NAME_LENGTH = 150


class User(AbstractUser):
    """Модель пользователя с авторизацией по email."""

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
    )
    first_name = models.CharField('Имя', max_length=MAX_NAME_LENGTH)
    last_name = models.CharField('Фамилия', max_length=MAX_NAME_LENGTH)
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        null=True,
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ('username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Возвращает username пользователя."""
        return self.username


class Subscription(models.Model):
    """Подписка пользователя на автора."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_subscription',
            ),
        )

    def __str__(self):
        """Возвращает связку подписчика и автора."""
        return f'{self.user} подписан на {self.author}'
