import math
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction

from recipes.models import Ingredient


@dataclass
class ShoppingLine:
    ingredient: Ingredient
    quantity: int


def calculate_shopping_list(plan):
    """Суммирует ингредиенты всех блюд плана с пересчётом на число порций.

    Расчёт идёт точными дробями (Fraction), чтобы ошибки округления не давали
    лишнюю единицу. Округляем вверх один раз, после суммирования.
    """
    totals = defaultdict(Fraction)
    ingredients = {}

    meals = plan.meals.select_related('recipe').prefetch_related('recipe__items__ingredient')
    for meal in meals:
        factor = Fraction(meal.servings, meal.recipe.servings)
        for item in meal.recipe.items.all():
            totals[item.ingredient_id] += Fraction(item.quantity) * factor
            ingredients[item.ingredient_id] = item.ingredient

    lines = [
        ShoppingLine(ingredient=ingredients[ingredient_id], quantity=math.ceil(total))
        for ingredient_id, total in totals.items()
    ]
    lines.sort(key=lambda line: (line.ingredient.category, line.ingredient.name))
    return lines
