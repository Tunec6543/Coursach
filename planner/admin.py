from django.contrib import admin

from .models import MealPlan, PlannedMeal


class PlannedMealInline(admin.TabularInline):
    model = PlannedMeal
    extra = 0


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'budget_limit', 'created_at')
    inlines = [PlannedMealInline]
