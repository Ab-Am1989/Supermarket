from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('customer/register/', views.register_customer, name='register_customer'),
    path('customer/list/', views.customer_list, name='customer_list'),
    path('customer/<int:customer_id>/', views.customer_details, name='customer_details'),
]
