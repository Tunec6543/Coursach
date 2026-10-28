from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from planner.models import MealPlan

from .forms import PantryItemForm
from .models import PantryItem
from .services import calculate_shopping_list


@login_required
def shopping_list(request):
    plan = MealPlan.objects.filter(user=request.user).first()
    lines = calculate_shopping_list(plan) if plan else []
    return render(request, 'shopping/list.html', {
        'plan': plan,
        'buy_lines': [line for line in lines if line.to_buy > 0],
        'covered_lines': [line for line in lines if line.to_buy == 0],
    })


@login_required
def pantry(request):
    if request.method == 'POST':
        form = PantryItemForm(request.POST)
        if form.is_valid():
            PantryItem.objects.update_or_create(
                user=request.user,
                ingredient=form.cleaned_data['ingredient'],
                defaults={'quantity': form.cleaned_data['quantity']},
            )
            return redirect('shopping:pantry')
    else:
        form = PantryItemForm()
    items = PantryItem.objects.filter(user=request.user).select_related('ingredient')
    return render(request, 'shopping/pantry.html', {'form': form, 'items': items})


@login_required
@require_POST
def pantry_delete(request, pk):
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)
    item.delete()
    return redirect('shopping:pantry')
