from django.shortcuts import get_object_or_404, render

from .models import Recipe


def recipe_list(request):
    recipes = Recipe.objects.all()
    hidden_count = 0
    show_all = request.GET.get('all') == '1'

    if request.user.is_authenticated and not show_all:
        profile = getattr(request.user, 'profile', None)
        if profile is not None:
            excluded = profile.excluded_ingredients.all()
            if excluded.exists():
                filtered = recipes.exclude(ingredients__in=excluded).distinct()
                hidden_count = recipes.count() - filtered.count()
                recipes = filtered

    return render(request, 'recipes/recipe_list.html', {
        'recipes': recipes,
        'hidden_count': hidden_count,
        'show_all': show_all,
    })

def recipe_detail(request, pk):
    recipe = get_object_or_404(
        Recipe.objects.prefetch_related('items__ingredient'),
        pk=pk,
    )
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})
