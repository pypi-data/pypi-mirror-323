from django import template
from ..models import Expense
from ..utils import get_balance

register = template.Library()


@register.inclusion_tag("balance.html")
def show_balance(original):
    # If original is not None we are in a change_view context.
    if original:
        expenses = original.expenses.all()
    # Otherwise it's a add_view context and we use all unprocessed expenses.
    else:
        expenses = Expense.objects.filter(calculation=None)
    balance = get_balance(expenses)
    return dict(
        expenses = expenses,
        balance = balance,
    )
