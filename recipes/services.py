def exclude_blocked(recipes, profile):
    """Убирает рецепты, содержащие запрещённые профилем ингредиенты."""
    blocked = profile.blocked_ingredient_ids()
    if blocked:
        recipes = recipes.exclude(ingredients__in=blocked)
    return recipes
