from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from recipes.models import Recipe


class MealPlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meal_plans',
    )
    start_date = models.DateField('Дата начала')
    budget_limit = models.DecimalField('Лимит бюджета, ₽', max_digits=8, decimal_places=2)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'План питания'
        verbose_name_plural = 'Планы питания'

    def __str__(self):
        return f'План {self.user.username} с {self.start_date}'


class PlannedMeal(models.Model):
    BREAKFAST, LUNCH, DINNER = 'breakfast', 'lunch', 'dinner'
    MEAL_TYPE_CHOICES = [
        (BREAKFAST, 'Завтрак'),
        (LUNCH, 'Обед'),
        (DINNER, 'Ужин'),
    ]

    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='meals')
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT, related_name='planned_meals')
    date = models.DateField('Дата')
    meal_type = models.CharField('Приём пищи', max_length=10, choices=MEAL_TYPE_CHOICES, default=DINNER)
    servings = models.PositiveSmallIntegerField('Порций', validators=[MinValueValidator(1)])

    class Meta:
        ordering = ['date']
        verbose_name = 'Блюдо в плане'
        verbose_name_plural = 'Блюда в плане'
        constraints = [
            models.UniqueConstraint(
                fields=['meal_plan', 'date', 'meal_type'],
                name='unique_meal_per_slot',
            ),
        ]

    def __str__(self):
        return f'{self.date}: {self.recipe.title}'
