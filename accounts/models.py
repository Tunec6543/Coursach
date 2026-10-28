from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from recipes.models import Ingredient


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
    excluded_ingredients = models.ManyToManyField(
        'recipes.Ingredient',
        verbose_name='Исключить ингредиенты',
        blank=True,
        related_name='excluded_by',
        help_text='Рецепты с этими ингредиентами не попадут в меню.',
    )
    allergens = models.ManyToManyField(
        'recipes.Allergen',
        verbose_name='Аллергии',
        blank=True,
        related_name='profiles',
        help_text='Рецепты с ингредиентами, содержащими эти аллергены, не попадут в меню.',
    )

    def blocked_ingredient_ids(self):
        """Единый источник правды: id ингредиентов, которые пользователю нельзя."""
        explicit = self.excluded_ingredients.values_list('id', flat=True)
        by_allergen = Ingredient.objects.filter(
            allergens__in=self.allergens.all()
        ).values_list('id', flat=True)
        return set(explicit) | set(by_allergen)
    def __str__(self):
        return f'Профиль {self.user.username}'
