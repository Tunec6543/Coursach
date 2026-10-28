from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from planner.models import MealPlan, PlannedMeal
from recipes.models import Ingredient, Recipe, RecipeIngredient

from .models import PantryItem
from .services import calculate_shopping_list


class ShoppingListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('tester', password='pass12345!')
        cls.rice = Ingredient.objects.create(name='Рис', unit='g', category='Крупы')
        cls.egg = Ingredient.objects.create(name='Яйцо', unit='pcs', category='Яйца')
        cls.salt = Ingredient.objects.create(name='Соль', unit='g', category='Специи')

    def make_recipe(self, title, servings, items):
        recipe = Recipe.objects.create(title=title, instructions='-', prep_time=10, servings=servings)
        for ingredient, quantity in items:
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, quantity=quantity)
        return recipe

    def make_plan(self, meals):
        """meals: список (рецепт, порции); по одному блюду в день."""
        plan = MealPlan.objects.create(user=self.user, start_date=date(2026, 10, 12), budget_limit=2500)
        for offset, (recipe, servings) in enumerate(meals):
            PlannedMeal.objects.create(
                meal_plan=plan, recipe=recipe, date=date(2026, 10, 12 + offset), servings=servings,
            )
        return plan

    def as_dict(self, lines):
        return {line.ingredient.name: line.to_buy for line in lines}

    def test_same_ingredient_is_summed(self):
        # пример из документа: 300 г + 200 г риса = 500 г
        a = self.make_recipe('A', 1, [(self.rice, 300)])
        b = self.make_recipe('B', 1, [(self.rice, 200)])
        plan = self.make_plan([(a, 1), (b, 1)])
        self.assertEqual(self.as_dict(calculate_shopping_list(plan)), {'Рис': 500})

    def test_scaling_by_servings(self):
        recipe = self.make_recipe('A', 2, [(self.rice, 300)])
        self.assertEqual(self.as_dict(calculate_shopping_list(self.make_plan([(recipe, 1)]))), {'Рис': 150})
        self.assertEqual(self.as_dict(calculate_shopping_list(self.make_plan([(recipe, 4)]))), {'Рис': 600})

    def test_same_recipe_twice_is_counted_twice(self):
        recipe = self.make_recipe('A', 1, [(self.rice, 100)])
        plan = self.make_plan([(recipe, 1), (recipe, 1)])
        self.assertEqual(self.as_dict(calculate_shopping_list(plan)), {'Рис': 200})

    def test_round_up_after_summing(self):
        # 3 яйца на 2 порции, готовим на 1 порцию: 1,5 + 1,5 = 3 (а не 2 + 2 = 4)
        recipe = self.make_recipe('A', 2, [(self.egg, 3)])
        plan = self.make_plan([(recipe, 1), (recipe, 1)])
        self.assertEqual(self.as_dict(calculate_shopping_list(plan)), {'Яйцо': 3})

    def test_single_fraction_rounds_up(self):
        recipe = self.make_recipe('A', 2, [(self.egg, 3)])
        plan = self.make_plan([(recipe, 1)])
        self.assertEqual(self.as_dict(calculate_shopping_list(plan)), {'Яйцо': 2})

    def test_exact_result_is_not_rounded_up(self):
        # 3 * 2/3 = ровно 2, лишней единицы быть не должно
        recipe = self.make_recipe('A', 3, [(self.egg, 3)])
        plan = self.make_plan([(recipe, 2)])
        self.assertEqual(self.as_dict(calculate_shopping_list(plan)), {'Яйцо': 2})

    def test_empty_plan(self):
        plan = MealPlan.objects.create(user=self.user, start_date=date(2026, 10, 12), budget_limit=2500)
        self.assertEqual(calculate_shopping_list(plan), [])

    def test_sorted_by_category_then_name(self):
        recipe = self.make_recipe('A', 1, [(self.salt, 3), (self.egg, 2), (self.rice, 100)])
        lines = calculate_shopping_list(self.make_plan([(recipe, 1)]))
        self.assertEqual([line.ingredient.name for line in lines], ['Рис', 'Соль', 'Яйцо'])

    def test_pantry_is_subtracted(self):
        # пример из документа: нужно 500 г, дома 150 г, купить 350 г
        a = self.make_recipe('A', 1, [(self.rice, 300)])
        b = self.make_recipe('B', 1, [(self.rice, 200)])
        PantryItem.objects.create(user=self.user, ingredient=self.rice, quantity=150)
        line = calculate_shopping_list(self.make_plan([(a, 1), (b, 1)]))[0]
        self.assertEqual((line.required, int(line.in_stock), line.to_buy), (500, 150, 350))

    def test_pantry_covers_need(self):
        recipe = self.make_recipe('A', 1, [(self.rice, 200)])
        PantryItem.objects.create(user=self.user, ingredient=self.rice, quantity=1000)
        line = calculate_shopping_list(self.make_plan([(recipe, 1)]))[0]
        self.assertEqual(line.to_buy, 0)

    def test_pantry_fraction_rounds_up(self):
        # нужно 1,5 яйца, дома 1 -> докупить 0,5 -> 1 шт
        recipe = self.make_recipe('A', 2, [(self.egg, 3)])
        PantryItem.objects.create(user=self.user, ingredient=self.egg, quantity=1)
        line = calculate_shopping_list(self.make_plan([(recipe, 1)]))[0]
        self.assertEqual(line.to_buy, 1)

    def test_other_users_pantry_ignored(self):
        other = User.objects.create_user('other', password='pass12345!')
        PantryItem.objects.create(user=other, ingredient=self.rice, quantity=1000)
        recipe = self.make_recipe('A', 1, [(self.rice, 200)])
        line = calculate_shopping_list(self.make_plan([(recipe, 1)]))[0]
        self.assertEqual(line.to_buy, 200)


class ShoppingViewTests(TestCase):
    def test_login_required(self):
        response = self.client.get(reverse('shopping:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_page_without_plan(self):
        User.objects.create_user('tester', password='pass12345!')
        self.client.login(username='tester', password='pass12345!')
        response = self.client.get(reverse('shopping:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Сначала составьте меню')

    def test_page_shows_items_and_units(self):
        user = User.objects.create_user('tester', password='pass12345!')
        rice = Ingredient.objects.create(name='Рис', unit='g', category='Крупы')
        recipe = Recipe.objects.create(title='A', instructions='-', prep_time=5, servings=1)
        RecipeIngredient.objects.create(recipe=recipe, ingredient=rice, quantity=200)
        plan = MealPlan.objects.create(user=user, start_date=date(2026, 10, 12), budget_limit=2500)
        PlannedMeal.objects.create(meal_plan=plan, recipe=recipe, date=date(2026, 10, 12), servings=1)
        self.client.login(username='tester', password='pass12345!')
        response = self.client.get(reverse('shopping:list'))
        self.assertContains(response, 'Рис')
        self.assertContains(response, '200 г')

    def test_other_users_plan_not_shown(self):
        owner = User.objects.create_user('owner', password='pass12345!')
        rice = Ingredient.objects.create(name='Рис', unit='g', category='Крупы')
        recipe = Recipe.objects.create(title='A', instructions='-', prep_time=5, servings=1)
        RecipeIngredient.objects.create(recipe=recipe, ingredient=rice, quantity=200)
        plan = MealPlan.objects.create(user=owner, start_date=date(2026, 10, 12), budget_limit=2500)
        PlannedMeal.objects.create(meal_plan=plan, recipe=recipe, date=date(2026, 10, 12), servings=1)
        User.objects.create_user('other', password='pass12345!')
        self.client.login(username='other', password='pass12345!')
        response = self.client.get(reverse('shopping:list'))
        self.assertNotContains(response, 'Рис')


class PantryViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='pass12345!')
        self.rice = Ingredient.objects.create(name='Рис', unit='g', category='Крупы')
        self.client.login(username='tester', password='pass12345!')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse('shopping:pantry'))
        self.assertEqual(response.status_code, 302)

    def test_add_then_update_does_not_duplicate(self):
        url = reverse('shopping:pantry')
        self.client.post(url, {'ingredient': self.rice.pk, 'quantity': '150'})
        self.client.post(url, {'ingredient': self.rice.pk, 'quantity': '400'})
        items = PantryItem.objects.filter(user=self.user)
        self.assertEqual(items.count(), 1)
        self.assertEqual(int(items[0].quantity), 400)

    def test_invalid_quantity_rejected(self):
        for bad in ('0', '-5', ''):
            response = self.client.post(reverse('shopping:pantry'), {'ingredient': self.rice.pk, 'quantity': bad})
            self.assertEqual(response.status_code, 200)
        self.assertEqual(PantryItem.objects.count(), 0)

    def test_delete_own_item(self):
        item = PantryItem.objects.create(user=self.user, ingredient=self.rice, quantity=100)
        self.client.post(reverse('shopping:pantry_delete', args=[item.pk]))
        self.assertEqual(PantryItem.objects.count(), 0)

    def test_cannot_delete_other_users_item(self):
        other = User.objects.create_user('other', password='pass12345!')
        item = PantryItem.objects.create(user=other, ingredient=self.rice, quantity=100)
        response = self.client.post(reverse('shopping:pantry_delete', args=[item.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(PantryItem.objects.count(), 1)

    def test_delete_requires_post(self):
        item = PantryItem.objects.create(user=self.user, ingredient=self.rice, quantity=100)
        response = self.client.get(reverse('shopping:pantry_delete', args=[item.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(PantryItem.objects.count(), 1)
