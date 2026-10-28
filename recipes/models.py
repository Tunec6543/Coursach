from django.core.validators import MinValueValidator
from django.db import models

class Allergen(models.Model):
    name = models.CharField('Название', max_length=50, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Аллерген'
        verbose_name_plural = 'Аллергены'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('g', 'г'),
        ('ml', 'мл'),
        ('pcs', 'шт'),
    ]

    name = models.CharField('Название', max_length=100, unique=True)
    unit = models.CharField('Единица измерения', max_length=3, choices=UNIT_CHOICES, default='g')
    category = models.CharField('Категория', max_length=50, blank=True)

    allergens = models.ManyToManyField(
        Allergen,
        verbose_name='Аллергены',
        blank=True,
        related_name='ingredients',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    instructions = models.TextField('Инструкция')
    prep_time = models.PositiveSmallIntegerField('Время приготовления, мин')
    servings = models.PositiveSmallIntegerField(
        'Порций в рецепте',
        default=1,
        validators=[MinValueValidator(1)],
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity = models.DecimalField(
        'Количество',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_per_recipe',
            ),
        ]

    def __str__(self):
        return f'{self.ingredient.name}: {self.quantity} {self.ingredient.unit}'
