from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from planner.models import MealPlan

from .services import calculate_shopping_list


@login_required
def shopping_list(request):
    plan = MealPlan.objects.filter(user=request.user).first()
    lines = calculate_shopping_list(plan) if plan else []
    return render(request, 'shopping/list.html', {'plan': plan, 'lines': lines})
