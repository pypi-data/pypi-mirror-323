from django.contrib import admin
from django.utils.translation import gettext as _
from django.contrib.messages import constants as messages
from .models import Calculation
from .models import Expense
from .forms import ExpenseForm


@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    """
    Modeladmin for calculations.
    """
    readonly_fields = ['created_on']
    list_display = ['created_on']
    list_filter = ['created_on']

    def has_change_permission(*args, **kwargs):
        return False

    def add_view(self, request, form_url="", extra_context=None):
        extra = extra_context or {}
        extra['hide_submit_row'] = not Expense.objects.filter(calculation=None).exists()
        return super().add_view(request, form_url, extra_context=extra)

    def save_model(self, request, obj, form, change):
            """
            Add all expenses whithout calculation.
            """
            expenses = list(Expense.objects.filter(calculation=None))
            if expenses:
                super().save_model(request, obj, form, change)
                obj.expenses.add(*expenses)
            else:
                self.message_user(request, _("There are no open expenses."), messages.ERROR)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """
    Modeladmin for expenses.
    """
    form = ExpenseForm
    list_select_related = True
    fieldsets = (
        (None, {
            "fields": ['amount', 'paid_for'],
        }),
        (_('Advanced Options'), {
            "classes": ["collapse"],
            "fields": ['info', 'paid_on'],
        }),
    )
    list_display = [
        'amount',
        'paid_by',
        'paid_on',
        ]
    list_filter = [
        'paid_by',
        'paid_for',
        'paid_on',
        'calculation',
        ]

    def save_model(self, request, obj, form, change):
        """
        Set paid_by to current user.
        """
        if not hasattr(obj, 'paid_by'):
            obj.paid_by = request.user
        super().save_model(request, obj, form, change)
