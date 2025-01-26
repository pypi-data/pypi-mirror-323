from django import forms
from django.contrib.auth.models import User
from .models import Expense


class ExpenseForm(forms.ModelForm):
    paid_for = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        initial=User.objects.all())
    class Meta:
        model = Expense
        fields = '__all__'
