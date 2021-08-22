from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from market.models import Customer
from django.db.utils import IntegrityError
from django.utils.datastructures import MultiValueDictKeyError
from django.db.models import Q


# Create your views here.
def register_customer(request):
    try:
        assert request.POST['password'] != '', 'You must enter your password'
        assert request.POST['email'] != '', 'You must enter your email address'
        new_user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'],
                                            password=request.POST['password'])
        new_user.first_name = request.POST['first_name']
        new_user.last_name = request.POST['last_name']
        new_user.save()
        new_customer = Customer.objects.create(user=new_user, phone=request.POST['phone'],
                                               address=request.POST['address'])

    except IntegrityError:
        data = dict(message='Username already exists!')
        response = JsonResponse(data)
        response.status_code = 400
        return response
    except (ValueError, AssertionError, MultiValueDictKeyError):
        data = dict(message='You sent the request with improper method or did not send necessary information')
        response = JsonResponse(data)
        response.status_code = 400
        return response
    else:
        data = dict(id=new_customer.id)
        response = JsonResponse(data)
        response.status_code = 201
        return response


def customer_list(request):
    if request.method == 'GET':
        customers_all = Customer.objects.all()
        customers = list()
        if request.GET.get('search'):
            customers_all = Customer.objects.filter(Q(user__username__contains=request.GET['search']) | Q(
                user__first_name__contains=request.GET['search']) | Q(
                user__last_name__contains=request.GET['search']) | Q(
                address__contains=request.GET['search']))
        for customer in customers_all:
            customer_specifications = {
                'id': customer.id,
                'username': customer.user.username,
                'first_name': customer.user.first_name,
                'last_name': customer.user.last_name,
                'email': customer.user.email,
                'phone': customer.phone,
                'address': customer.address,
                'balance': customer.balance,
            }
            customers.append(customer_specifications)
        data = dict(customers=customers)
        return JsonResponse(data)
    else:
        response = JsonResponse(dict(message='You must send request only with GET method!'))
        response.status_code = 400
        return response