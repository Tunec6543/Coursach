import random
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from accounts.models import Profile
from recipes.models import Recipe

from .models import MealPlan, PlannedMeal

DAYS_IN_PLAN = 7


class NoSuitableRecipes(Exception):
    """Нет ни одного рецепта, подходящего под ограничения пользователя."""


def get_suitable_recipes(profile):
    """Рецепты с известным составом, без исключённых пользователем ингредиентов."""
    recipes = Recipe.objects.filter(items__isnull=False)
    excluded = profile.excluded_ingredients.all()
    if excluded.exists():
        recipes = recipes.exclude(ingredients__in=excluded)
    return list(recipes.distinct())


def pick_recipes(candidates, days, rng):
    """Выбирает рецепты на days дней: без повторов подряд, пока хватает рецептов."""
    chosen = []
    while len(chosen) < days:
        batch = candidates[:]
        rng.shuffle(batch)
        # не ставим один и тот же рецепт в соседние дни на стыке двух кругов
        if chosen and len(batch) > 1 and batch[0] == chosen[-1]:
            batch.append(batch.pop(0))
        chosen.extend(batch)
    return chosen[:days]


@transaction.atomic
def generate_meal_plan(user, start_date=None, days=DAYS_IN_PLAN, rng=None):
    rng = rng or random.Random()
    profile, _ = Profile.objects.get_or_create(user=user)

    candidates = get_suitable_recipes(profile)
    if not candidates:
        raise NoSuitableRecipes

    start_date = start_date or timezone.localdate()
    plan = MealPlan.objects.create(
        user=user,
        start_date=start_date,
        budget_limit=profile.weekly_budget,
    )
    PlannedMeal.objects.bulk_create([
        PlannedMeal(
            meal_plan=plan,
            recipe=recipe,
            date=start_date + timedelta(days=offset),
            servings=profile.servings,
        )
        for offset, recipe in enumerate(pick_recipes(candidates, days, rng))
    ])
    return plan
