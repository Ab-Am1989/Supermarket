from django.urls import path

from . import views

app_name = 'market'
urlpatterns = [
    # products urls
    path('product/insert/', views.product_insert, name='product_insert'),
    path('product/list/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_details, name='product_details'),
    path('product/<int:product_id>/edit_inventory/', views.edit_inventory, name='edit_inventory'),
    # TODO: insert other url paths
    # path(...
    # path(...
    # path(...
]
