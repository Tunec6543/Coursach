from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    weekly_budget = models.DecimalField(
        'Бюджет на неделю, ₽',
        max_digits=8,
        decimal_places=2,
        default=2500,
        validators=[MinValueValidator(0)],
    )
    servings = models.PositiveSmallIntegerField(
        'Количество порций',
        default=1,
        validators=[MinValueValidator(1)],
    )

    def __str__(self):
        return f'Профиль {self.user.username}'
