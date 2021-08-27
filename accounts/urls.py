from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('customer/register/', views.register_customer, name='register_customer'),
    path('customer/list/', views.customer_list, name='customer_list'),
    path('customer/<int:customer_id>/', views.customer_details, name='customer_details'),
    path('customer/<int:customer_id>/edit/', views.customer_edit, name='customer_edit'),
    path('customer/login/', views.login_view, name='login_view'),
    path('customer/logout/', views.logout_view, name='logout_view'),
]
