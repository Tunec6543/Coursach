from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['weekly_budget', 'servings', 'excluded_ingredients']
        widgets = {'excluded_ingredients': forms.CheckboxSelectMultiple}
