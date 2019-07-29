from django.db import models
from decimal import Decimal
import datetime
from django.core.validators import validate_email
from operator import itemgetter as ig
from django.core.mail import send_mail


class MyDecimal(Decimal):
    def __repr__(self):
        return str(float(self))


class Commission_plan(models.Model):
    lower_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="lo")
    upper_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="up")
    min_value = models.DecimalField(max_digits=19, decimal_places=2, verbose_name="min")

    def __srt__(self):
        return self.id


class Sellers(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    age = models.IntegerField()
    email = models.EmailField(max_length=100, blank=False, unique=True, validators=[validate_email])
    cpf = models.CharField(max_length=11, unique=True)
    plan = models.ForeignKey(Commission_plan, on_delete=models.CASCADE, verbose_name="plan")

    def __str__(self):
        return self.name


class Sales(models.Model):
    MONTHS = (
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    )

    month = models.IntegerField(choices=MONTHS)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    sellers_id = models.ForeignKey(Sellers, on_delete=models.CASCADE, primary_key=False, verbose_name="sid")
    commission = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return "Seller: %s" % self.sellers_id.name

    def calc_commission(self, seller, amount):
        if not Sellers.objects.filter(id=seller):
            return 404
        else:
            sel_calc = Sellers.objects.get(id=seller)
            dec_amount = MyDecimal(amount)
            if dec_amount <= MyDecimal(sel_calc.plan.min_value):
                commission = dec_amount * MyDecimal(sel_calc.plan.lower_percentage / 100)
            else:
                commission = dec_amount * MyDecimal(sel_calc.plan.upper_percentage / 100)
        return MyDecimal(round(commission, 2))

    def sales_month(self, seller, amount, month):
        if not Sales.objects.filter(month=month):
            sel_month = Sellers.objects.get(id=seller)
            month_amount = MyDecimal(amount)
            s = Sales(sellers_id=sel_month, amount=month_amount, month=month)
            s.commission = self.calc_commission(seller, month_amount)
            s.save()
            return {"id": s.id, "commission": MyDecimal(s.commission)}

        else:
            return 409

    def return_sellers(self, month):
        if not Sales.objects.filter(month=month):
            return 404
        else:
            s = Sales.objects.select_related('sellers_id').filter(month=month)
            return sorted([{"name": i.sellers_id.name, "id": i.sellers_id.id, "commission": MyDecimal(i.commission)}
                           for i in s], key=lambda x: x['commission'], reverse=True)

    def notify_seller(self, seller, month):
        if not Sales.objects.filter(sellers_id=seller, month=month):
            return 404
        else:
            send_mail(
                'Notificação - valor de vendas',
                'Suas vendas no mês estão abaixo da média mensal.',
                'commission_admin@mail.com',
                [Sales.objects.get(sellers_id=seller, month=month).sellers_id.email],
                fail_silently=False
            )

    def check_commission(self, seller, amount):
        month = datetime.datetime.now().month
        db_fetch = Sales.objects.select_related('sellers_id').filter(sellers_id=seller)
        if not db_fetch:
            return 404
        else:
            for i in range(len(db_fetch)):
                if db_fetch[i].month == month:
                    db_fetch[i].amount = MyDecimal(amount)
                    db_fetch[i].commission = self.calc_commission(seller, amount)
                db_fetch.order_by('-commission')
            avg_sales = (sum([db_fetch[i].amount * (len(db_fetch) - i) for i in range(len(db_fetch))]) /
                         sum([len(db_fetch) - i for i in range(len(db_fetch))]))
            cut_amount = avg_sales - (avg_sales * 10 / 100)
            notify = ([db_fetch[i].amount for i in range(len(db_fetch)) if db_fetch[i].amount < cut_amount and
                       db_fetch[i].month == month])
            if not notify:
                out_message = {"seller_notified": False}
            else:
                out_message = {"seller_notified": True}
                self.notify_seller(seller, month)
            return out_message
