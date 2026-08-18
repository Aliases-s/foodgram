"""Настройки админ-зоны приложения users."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users.models import Subscription

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка модели пользователя."""

    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'username')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка модели подписки."""

    list_display = ('user', 'author')
