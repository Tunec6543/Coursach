import math
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

from recipes.models import Ingredient

from .models import PantryItem


@dataclass
class ShoppingLine:
    ingredient: Ingredient
    required: int      # нужно по меню (округлено вверх)
    in_stock: Decimal  # есть дома
    to_buy: int        # нужно купить (округлено вверх)


def calculate_shopping_list(plan):
    """Считает, что нужно купить для плана: меню минус домашний запас.

    Расчёт идёт точными дробями (Fraction), чтобы ошибки округления не давали
    лишнюю единицу. Округляем вверх один раз, после суммирования и вычитания.
    """
    required = defaultdict(Fraction)
    ingredients = {}

    meals = plan.meals.select_related('recipe').prefetch_related('recipe__items__ingredient')
    for meal in meals:
        factor = Fraction(meal.servings, meal.recipe.servings)
        for item in meal.recipe.items.all():
            required[item.ingredient_id] += Fraction(item.quantity) * factor
            ingredients[item.ingredient_id] = item.ingredient

    stock = {
        item.ingredient_id: item.quantity
        for item in PantryItem.objects.filter(user=plan.user)
    }

    lines = []
    for ingredient_id, total in required.items():
        in_stock = stock.get(ingredient_id, Decimal(0))
        lines.append(ShoppingLine(
            ingredient=ingredients[ingredient_id],
            required=math.ceil(total),
            in_stock=in_stock,
            to_buy=math.ceil(max(total - Fraction(in_stock), 0)),
        ))
    lines.sort(key=lambda line: (line.ingredient.category, line.ingredient.name))
    return lines
