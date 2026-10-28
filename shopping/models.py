from django.db import models

# Create your models here.
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from recipes.models import Ingredient


class PantryItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pantry_items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='pantry_items')
    quantity = models.DecimalField(
        'Количество',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )

    class Meta:
        ordering = ['ingredient__name']
        verbose_name = 'Продукт в запасе'
        verbose_name_plural = 'Домашний запас'
        constraints = [
            models.UniqueConstraint(fields=['user', 'ingredient'], name='unique_pantry_item'),
        ]

    def __str__(self):
        return f'{self.ingredient.name}: {self.quantity}'
