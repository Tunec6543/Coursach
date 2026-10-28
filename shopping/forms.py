from django import forms

from .models import PantryItem


class PantryItemForm(forms.ModelForm):
    class Meta:
        model = PantryItem
        fields = ['ingredient', 'quantity']
        labels = {'ingredient': 'Продукт', 'quantity': 'Сколько есть дома'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].label_from_instance = (
            lambda obj: f'{obj.name}, {obj.get_unit_display()}'
        )
