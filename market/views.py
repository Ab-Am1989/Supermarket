"""
    You can define utility functions here if needed
    For example, a function to create a JsonResponse
    with a specified status code or a message, etc.

    DO NOT FORGET to complete url patterns in market/urls.py
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from market.models import Product
from django.http import HttpResponse


def product_insert(request):
    # hint: you should check request method like below
    try:
        # inventory = 1
        # if request.POST['inventory'] is not None:
        #     inventory = int(request.POST['inventory'])
        tmp = request.POST.get('inventory', None)
        if tmp is not None:
            new_product = Product.objects.create(code=request.POST['code'], name=request.POST['name'],
                                                 price=int(request.POST['price']),
                                                 inventory=int(request.POST['inventory']))
        else:
            new_product = Product.objects.create(code=request.POST['code'], name=request.POST['name'],
                                                 price=int(request.POST['price']))
        data = {
            "id": new_product.id
        }
        response = JsonResponse(data)
        response.status_code = 201
        return response
    except Exception as e:
        data = {
            "message": str(e)
        }
        response = JsonResponse(data)
        response.status_code = 400
        return response


def product_list(request):
    products_all = Product.objects.all()
    if request.GET.get('search'):
        products_all = Product.objects.filter(name__contains=request.GET.get('search'))
    products = []
    for product in products_all:
        product_details = {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'price': product.price,
            'inventory': product.inventory,
            }
        products.append(product_details)
    data = {
        'products': products
    }
    response = JsonResponse(data)
    response.status_code = 200
    return response


def product_details(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
        data = {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'price': product.code,
            'inventory': product.inventory
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response
    except Exception:
        data = dict(message='Product Not Found!')
        response = JsonResponse(data)
        response.status_code = 404
        return response


def edit_inventory(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
        amount = int(request.POST.get('amount', None))
        if int(amount) >= 0:
            product.increase_inventory(int(amount))
        else:
            assert product.inventory > int(amount) * (-1), 'Not enough inventory!'
            product.decrease_inventory(int(amount) * (-1))
        data = {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'price': product.price,
            'inventory': product.inventory,
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response
    except AssertionError as ae:
        data = {
            'message': str(ae)
        }
        response = JsonResponse(data)
        response.status_code = 400
        return response
    except (ValueError, TypeError) as ts:
        data = {
            'message': 'Please Enter a correct amount of product!'
        }
        response = JsonResponse(data)
        response.status_code = 400
        return response
    except Product.DoesNotExist as pe:
        data = {
            'message': 'Product Not Found!'
        }
        response = JsonResponse(data)
        response.status_code = 404
        return response
