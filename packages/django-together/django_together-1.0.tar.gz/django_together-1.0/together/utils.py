
def get_balance(expenses):
    """
    Calculate expenses and return the balance for each user.
    """
    balance = dict()
    for expense in expenses:
        paid_for = list(expense.paid_for.all())
        # All users start with zero.
        for user in set([expense.paid_by, *paid_for]):
            if not user in balance.keys():
                balance[user] = 0

        # Sum up their expenses.
        balance[expense.paid_by] += expense.amount

        # Pull off their debts.
        for user in paid_for:
            splitted_amount = round(expense.amount / len(paid_for), 2)
            balance[user] -= splitted_amount

    return balance

