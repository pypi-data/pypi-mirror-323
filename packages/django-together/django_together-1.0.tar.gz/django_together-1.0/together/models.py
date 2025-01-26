from django.db import models
from django.utils import timezone
from django.utils.formats import localize
from django.utils.translation import gettext as _
from django.contrib.auth.models import User


class Calculation(models.Model):
    """
    A group of expenses that should be calculated.
    """
    created_on = models.DateTimeField(verbose_name=_('Created on'), auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return _('Calculation from %(created_on)s') % {'created_on': localize(self.created_on)}


class ExpenseManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().select_related('paid_by', 'calculation')
        qs = qs.prefetch_related('paid_for')
        return qs


class Expense(models.Model):
    """
    Simple expense model.
    """
    objects = ExpenseManager()
    amount = models.DecimalField(
        verbose_name=_('Amount'),
        max_digits=6,
        decimal_places=2)
    paid_by = models.ForeignKey(
        User,
        verbose_name=_('Paid by'),
        on_delete=models.CASCADE,
        related_name='paid_by_expenses')
    paid_for = models.ManyToManyField(
        User,
        verbose_name=_('Paid for'),
        related_name='paid_for_expenses')
    paid_on = models.DateTimeField(
        verbose_name=_('Paid on'),
        blank=True,
        default=timezone.now )
    info = models.TextField(_('Info'), blank=True)
    calculation = models.ForeignKey(
        Calculation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Calculation'),
        related_name='expenses',
        editable=False)

    class Meta:
        ordering = ['-paid_on', 'paid_by']

    def __str__(self):
        return _('%(user)s paid %(amount)s (%(paid_on)s)') % {
            'paid_on': localize(self.paid_on),
            'user': self.paid_by,
            'amount': self.amount}