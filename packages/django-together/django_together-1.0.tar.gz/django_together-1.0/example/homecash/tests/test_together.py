
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from together.models import Expense
from together.models import Calculation
from together.utils import get_balance
from together.__version__ import __version__


class CalculationTestCase(TestCase):
    fixtures = [settings.BASE_DIR / 'fixtures/testdata']

    def setUp(self):
        self.admin = User.objects.get(username='admin')
        self.harold = User.objects.get(username='harold')
        self.client.force_login(self.harold)

    def test_01_expense_initial_data(self):
        """
        Check initial data for paid_for field.
        """
        add_url = reverse('admin:together_expense_add')
        response = self.client.get(add_url)
        self.assertEqual(response.status_code, 200)
        for i in range(2):
            self.assertContains(response, f'id="id_paid_for_{i}" checked'.encode())

    def test_02_expense_paid_by(self):
        """
        Check if expenses are saved with the current user as paid_by field.
        """
        add_url = reverse('admin:together_expense_add')
        data = dict(
            amount=222.22,
            paid_for=User.objects.all().values_list('id', flat=True)
        )
        response = self.client.post(add_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        expense = Expense.objects.get(paid_by=self.harold, amount=222.22)
        self.assertEqual(expense.paid_by, self.harold)

    def test_03_calculation_add_form(self):
        """
        Check if the balance and open expenses are rendered on calculation add
        form.
        """
        add_url = reverse('admin:together_calculation_add')
        response = self.client.get(add_url)
        self.assertEqual(response.status_code, 200)

        # Check if the balance was rendered.
        open_expenses = Expense.objects.filter(calculation=None)
        balance = get_balance(open_expenses)
        for user, amount in balance.items():
            self.assertContains(response, user.username.encode())
            self.assertContains(response, str(amount).encode())

        # Check if the expenses are listed.
        for expense in open_expenses:
            self.assertContains(response, str(expense).encode())

    def test_04_calculation_change_form(self):
        """
        Check if the balance and open expenses are rendered on calculation
        change form.
        """
        calculation = Calculation.objects.all().first()
        change_url = reverse(
            'admin:together_calculation_change',
            kwargs=dict(object_id=calculation.id))
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)

        # Check if the balance was rendered.
        expenses = calculation.expenses.all()
        balance = get_balance(expenses)
        for user, amount in balance.items():
            self.assertContains(response, user.username.encode())
            self.assertContains(response, str(amount).encode())

        # Check if the expenses are listed.
        for expense in expenses:
            self.assertContains(response, str(expense).encode())

    def test_04_calculation_on_save(self):
        """
        Check if all open expenses are added to newly created calculation.
        """
        open_expenses = list(Expense.objects.filter(calculation=None))
        add_url = reverse('admin:together_calculation_add')
        response = self.client.post(add_url, follow=True)
        self.assertEqual(response.status_code, 200)
        calculation = Calculation.objects.all().first()
        self.assertListEqual(list(calculation.expenses.all()), open_expenses)
        self.assertFalse(Expense.objects.filter(calculation=None))

    def test_05_calculation_on_save_without_expenses(self):
        """
        Check if saving a calculation is prevented if no open expenses exists.
        """
        calculations_before = Calculation.objects.all().count()
        Expense.objects.all().delete()
        add_url = reverse('admin:together_calculation_add')
        response = self.client.post(add_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no open expenses.")
        calculations_after = Calculation.objects.all().count()
        self.assertEqual(calculations_before, calculations_after)

    def test_06_calculation_add_form_without_expenses(self):
        """
        Check if saving a calculation is prevented if no open expenses exists.
        """
        Expense.objects.all().delete()
        add_url = reverse('admin:together_calculation_add')
        response = self.client.get(add_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no open expenses.")
