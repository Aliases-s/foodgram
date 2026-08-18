"""Кастомные поля сериализаторов."""

import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Поле картинки, принимающее строку в формате base64."""

    def to_internal_value(self, data):
        """Декодирует строку base64 в файл."""
        if isinstance(data, str) and data.startswith("data:image"):
            header, encoded = data.split(";base64,")
            extension = header.split("/")[-1]
            data = ContentFile(
                base64.b64decode(encoded),
                name=f"{uuid.uuid4()}.{extension}",
            )
        return super().to_internal_value(data)
