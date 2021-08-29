from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.urls import reverse

from market.models import Customer
from django.db.utils import IntegrityError
from django.utils.datastructures import MultiValueDictKeyError
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


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


def customer_details(request, customer_id):
    try:
        if request.method == 'POST':
            raise ValueError('Request method is improper!')
        else:
            customer = Customer.objects.get(pk=customer_id)
            data = {
                'id': customer.id,
                'username': customer.user.username,
                'first_name': customer.user.first_name,
                'last_name': customer.user.last_name,
                'email': customer.user.email,
                'phone': customer.phone,
                'address': customer.address,
                'balance': customer.balance,
            }
            response = JsonResponse(data)
            response.status_code = 200
            return response

    except Customer.DoesNotExist:
        response = JsonResponse(dict(message='Customer Not Found.'))
        response.status_code = 404
        return response
    except ValueError as e:
        response = JsonResponse(dict(message=str(e)))
        response.status_code = 400
        return response


def customer_edit(request, customer_id):
    try:
        if not (request.method == 'POST'):
            raise AssertionError('Request method is improper!')
        else:
            customer = Customer.objects.get(pk=customer_id)
            if request.POST.get('id') or request.POST.get('username') or request.POST.get('password'):
                raise AssertionError('Cannot edit customer\'s identity and credentials.')
            if request.POST.get('first_name'):
                customer.user.first_name = request.POST.get('first_name')
            if request.POST.get('last_name'):
                customer.user.last_name = request.POST.get('last_name')
            if request.POST.get('email'):
                customer.user.email = request.POST.get('email')
            if request.POST.get('phone'):
                customer.phone = request.POST.get('phone')
            if request.POST.get('address'):
                customer.address = request.POST.get('address')
            if request.POST.get('balance'):
                customer.balance = int(request.POST.get('balance'))
            data = {
                "id": customer.id,
                "username": customer.user.username,
                "first_name": customer.user.first_name,
                "last_name": customer.user.last_name,
                "email": customer.user.email,
                "phone": customer.phone,
                "address": customer.address,
                "balance": customer.balance,
            }
            customer.user.save()
            customer.save()
            response = JsonResponse(data)
            response.status_code = 200
            return response
    except AssertionError as e:
        response = JsonResponse(dict(message=str(e)))
        response.status_code = 403
        return response
    except ValueError:
        response = JsonResponse(dict(message='Balance should be integer'))
        response.status_code = 400
        return response


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse(dict(message='You are logged in successfully.'))
        else:
            response: JsonResponse = JsonResponse(dict(message='Username or Password is incorrect.'))
            response.status_code = 404
            return response
    else:
        if request.user.is_authenticated:
            response = JsonResponse(dict(message='You have logged in.'))
            response.status_code = 200
            return response
        else:
            response = JsonResponse(dict(message='You are not logged in.'))
            response.status_code = 403
            return response


def logout_view(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
            response = JsonResponse(dict(message='You are logged out successfully.'))
            response.status_code = 200
            return response
        else:
            response = JsonResponse(dict(message='You are not logged in.'))
            response.status_code = 403
            return response
    else:
        response = JsonResponse(dict(message='You didn\'t use proper method please try again!'))
        response.status_code = 400
        return response


@login_required(login_url='accounts:login_view')
def profile_details(request):
    if request.method == 'POST':
        customer = request.user.customer
        data = {
            "id": customer.id,
            "username": customer.user.username,
            "first_name": customer.user.first_name,
            "last_name": customer.user.last_name,
            "email": customer.user.email,
            "phone": customer.phone,
            "address": customer.address,
            "balance": customer.balance,
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response

