"""
    You can define utility functions here if needed
    For example, a function to create a JsonResponse
    with a specified status code or a message, etc.

    DO NOT FORGET to complete url patterns in market/urls.py
"""
import json
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from market.models import Order, OrderRow, Customer, Product
from market.models import Product, Order


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


@login_required(login_url='accounts:login_view')
def show_cart(request):
    try:
        items = list()
        customer = request.user.customer
        customer_orders = Order.objects.get(Q(customer=customer) & Q(status=Order.STATUS_SHOPPING))
        order_rows = customer_orders.rows.all()
        for order in order_rows:
            order_specifications = {
                'code': order.product.code,
                'name': order.product.name,
                'price': order.product.price,
                'amount': order.amount,
            }
            items.append(order_specifications)

        data = {
            'total_price': customer_orders.total_price,
            'items': items,
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response
    except Order.DoesNotExist:
        data = {
            'total_price': 0,
            'items': items,
        }
        return JsonResponse(data)


@login_required(login_url='accounts:login_view')
def add_item(request):
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        items = list()
        errors = list()
        data = dict()
        for i in range(len(received_json_data)):
            try:
                code = received_json_data[i]['code']
                amount = received_json_data[i]['amount']
                customer = request.user.customer
                product = Product.objects.get(code=code)
                shopping_order = Order.objects.get(Q(customer=customer) & Q(status=Order.STATUS_SHOPPING))
                shopping_order.add_product(product=product, amount=int(amount))
                shopping_order_row = shopping_order.rows.get(product=product)
                successful_add = {
                    'code': shopping_order_row.product.code,
                    'name': shopping_order_row.product.name,
                    'price': shopping_order_row.product.price,
                    'amount': shopping_order_row.amount,
                }
                items.append(successful_add)
            except Order.DoesNotExist:
                new_order = Order.initiate(customer)
                new_order.add_product(product=product, amount=int(amount))
                new_order.save()
                new_order_row = new_order.rows.get(product=product)
                successful_add = {
                    'code': new_order_row.product.code,
                    'name': new_order_row.product.name,
                    'price': new_order_row.product.price,
                    'amount': new_order_row.amount,
                }
                items.append(successful_add)
            except (AssertionError, Product.DoesNotExist, ValueError) as e:
                errors.append({
                    'code': code,
                    'message': str(e),
                })

        if errors:
            data = {
                'errors': errors,
                'items': items,
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response
        else:

            return HttpResponseRedirect(reverse('market:show_cart'))

    else:
        response = JsonResponse(dict(message='Please retry with correct method'))
        response.status_code = 400
        return response
