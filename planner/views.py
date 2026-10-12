from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import MealPlan
from .services import NoSuitableRecipes, generate_meal_plan


def home(request):
    return render(request, 'planner/home.html')


@login_required
def plan_detail(request):
    plan = (
        MealPlan.objects.filter(user=request.user)
        .prefetch_related('meals__recipe')
        .first()
    )
    return render(request, 'planner/plan.html', {'plan': plan})


@login_required
@require_POST
def plan_create(request):
    try:
        generate_meal_plan(request.user)
    except NoSuitableRecipes:
        messages.error(
            request,
            'Не нашлось рецептов, подходящих под ваши исключения. Измените исключения в профиле.',
        )
    return redirect('planner:plan')
