from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


class Product(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    inventory = models.PositiveIntegerField(default=0)

    def increase_inventory(self, amount):
        self.inventory += amount
        self.save()

    def decrease_inventory(self, amount):
        self.inventory -= amount
        self.save()


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    balance = models.PositiveIntegerField(default=20000)

    def deposit(self, amount):
        self.balance += amount
        self.save()

    def spend(self, amount):
        self.balance -= amount


class OrderRow(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    order_in = models.ForeignKey('Order', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


class Order(models.Model):
    # Status values. DO NOT EDIT
    STATUS_SHOPPING = 1
    STATUS_SUBMITTED = 2
    STATUS_CANCELED = 3
    STATUS_SENT = 4
    STATUS_CHOICES = (
        (STATUS_SHOPPING, 'در حال خرید'),
        (STATUS_SUBMITTED, 'ثبت‌شده'),
        (STATUS_CANCELED, 'لغو‌شده'),
        (STATUS_SENT, 'ارسال‌شده'),
    )

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    order_time = models.DateTimeField(auto_now_add=True)
    total_price = models.PositiveIntegerField(default=0)
    status = models.IntegerField(choices=STATUS_CHOICES)
    rows = models.ManyToManyField('OrderRow', null=True, blank=True)

    @staticmethod
    def initiate(customer):
        orders_shopping = Order.objects.get(Q(customer=customer) & Q(status=Order.STATUS_SHOPPING))
        if orders_shopping is None:
            new_order = Order.objects.create(customer=customer, status=Order.STATUS_SHOPPING)
            new_order.save()
        return new_order

    def add_product(self, product, amount):
        product_row = Product.objects.get(pk=product.id)
        assert amount > 0, 'Number of product must be grater than 0'
        assert amount <= product_row.inventory, 'Enough number of this product does not exist'
        new_product = OrderRow.objects.create(product=product, amount=amount, order_in=self)
        new_product.save()
        self.rows.add(new_product)
        self.total_price += new_product.amount * new_product.product.price
        self.save()

    def remove_product(self, product, amount=None):
        product = OrderRow.objects.filter(product=product)
        if amount is not None:
            product.amount -= amount
            product.save()
        else:
            self.rows.remove(product)
            product.objects.delete()
        self.save()

    def submit(self):
        assert self.status is self.STATUS_SHOPPING, 'Order status must be equal with Shopping status!'
        total_price = 0
        for row in self.rows:
            assert row.amount <= row.product.inventory, 'Not enough product exist in inventory'
            total_price += row.amount * row.product.price
        self.total_price = total_price
        assert self.total_price <= self.customer.balance, 'The customer has not enough balance'
        self.customer.spend(self.total_price)
        for row in self.rows:
            row.product.decrease_inventory(row.amount)
        self.status = self.STATUS_SUBMITTED
        self.save()

    def cancel(self):
        assert self.status is self.STATUS_SUBMITTED, 'You cannot cancel the order that did not submitted '
        for row in self.rows:
            row.product.increase_inventory(row.amount)
        self.customer.balance += self.total_price
        self.status = self.STATUS_CANCELED
        self.save()

    def send(self):
        assert self.status is self.STATUS_SUBMITTED, 'You cannot send the order that did not submitted!'
        self.status = self.STATUS_SENT
        self.save()
