from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from market.models import Customer
from django.db.utils import IntegrityError
from django.utils.datastructures import MultiValueDictKeyError


# Create your views here.
def register_customer(request):
    if request.method == 'POST':
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
            data = dict(message='You are not enter your necessary information')
            response = JsonResponse(data)
            response.status_code = 400
            return response
        else:
            data = dict(id=new_customer.id)
            response = JsonResponse(data)
            response.status_code = 201
            return response
