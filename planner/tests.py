from django.contrib.auth.models import User
from django.test import TestCase

from recipes.models import Allergen, Ingredient, Recipe, RecipeIngredient

from .services import NoSuitableRecipes, generate_meal_plan, get_suitable_recipes


class BlockedIngredientsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('tester', password='pass12345!')
        cls.profile = cls.user.profile
        dairy = Allergen.objects.create(name='Молоко')
        cls.milk = Ingredient.objects.create(name='Молоко', unit='ml')
        cls.butter = Ingredient.objects.create(name='Масло', unit='g')
        cls.rice = Ingredient.objects.create(name='Рис', unit='g')
        cls.milk.allergens.add(dairy)
        cls.butter.allergens.add(dairy)
        cls.dairy = dairy
        for title, ingredient in [('Каша', cls.milk), ('Бутерброд', cls.butter), ('Рис', cls.rice)]:
            recipe = Recipe.objects.create(title=title, instructions='-', prep_time=5, servings=1)
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, quantity=100)

    def titles(self):
        return {r.title for r in get_suitable_recipes(self.profile)}

    def test_no_restrictions(self):
        self.assertEqual(self.titles(), {'Каша', 'Бутерброд', 'Рис'})

    def test_allergen_blocks_all_its_ingredients(self):
        self.profile.allergens.add(self.dairy)
        self.assertEqual(self.titles(), {'Рис'})

    def test_explicit_exclusion(self):
        self.profile.excluded_ingredients.add(self.rice)
        self.assertEqual(self.titles(), {'Каша', 'Бутерброд'})

    def test_everything_blocked_raises(self):
        self.profile.allergens.add(self.dairy)
        self.profile.excluded_ingredients.add(self.rice)
        with self.assertRaises(NoSuitableRecipes):
            generate_meal_plan(self.user)
