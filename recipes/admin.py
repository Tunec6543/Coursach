from django.contrib import admin

from .models import Allergen, Ingredient, Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 3


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'category')
    list_filter = ('category', 'allergens')
    search_fields = ('name',)
    filter_horizontal = ('allergens',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'prep_time', 'servings')
    search_fields = ('title',)
    inlines = [RecipeIngredientInline]
