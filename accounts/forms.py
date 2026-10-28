from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['weekly_budget', 'servings', 'allergens', 'excluded_ingredients']
        widgets = {
            'allergens': forms.CheckboxSelectMultiple,
            'excluded_ingredients': forms.CheckboxSelectMultiple,
        }
