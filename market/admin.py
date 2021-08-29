from django.contrib import admin

# Register your models here.
from market.models import Order, OrderRow, Customer, Product

admin.site.register(Order)
admin.site.register(Customer)
admin.site.register(OrderRow)
admin.site.register(Product)