from multiprocessing import context
from django.shortcuts import render
from rest_framework import status, permissions, generics, viewsets
from rest_framework.response import Response
from .serializers import RegisterCompanySerializer, RegisterDomainSerializer, RegisterSuperUserSerializer, RegisterUserSerializer, UserSerializer, TenantSerializer
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from knox.views import LoginView as KnoxLoginView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import login
from knox.models import AuthToken
from rest_framework.views import APIView
from .models import Tenant
from django.contrib.auth.models import User
import logging
db_logger = logging.getLogger('db')

# Create your views here.


# Login API
class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)


# Create Customer with auto create schema
@api_view(['POST'])
def create_company(request):
    if request.method == 'POST':
        company_data = JSONParser().parse(request)
        company_serializer = RegisterCompanySerializer(data=company_data)
        domain = company_data['domain_name']
        if company_serializer.is_valid():
            company_serializer.save()
            tenant = company_serializer.data['id']
            domain_data = {
                'domain': domain,
                'tenant' : tenant,
                'is_primary' : True
            }
            domain_serializers = RegisterDomainSerializer(data = domain_data)
            domain_serializers.is_valid()
            domain_serializers.save()
            return JsonResponse({'company' : company_serializer.data, 'domain' : domain_serializers.data}, status = status.HTTP_201_CREATED)
        return JsonResponse(company_serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_200_OK)


# Making Tenant Active or Inactive
class MakeUserActive(APIView):
    def post(self,request):
        if not request.user.id:
            return Response("Please Login", status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_superuser:
            return Response("You are not a super user", status=status.HTTP_401_UNAUTHORIZED)
        if not request.data:
            return Response("No content", status=status.HTTP_204_NO_CONTENT)
        cutomerId = request.data['customerId']
        isActive = request.data['is_active']
        customer = Tenant.objects.get(id = cutomerId)
        if(isActive == 0):
            customer.is_active = True
            customer.save()
            return Response("Customer activated successfully",status=status.HTTP_200_OK)
        elif(isActive == 1):
            customer.is_active = False
            customer.save()
            return Response("Customer Deactivated successfully",status=status.HTTP_200_OK)
        else:
            return Response("Invalid",status=status.HTTP_400_BAD_REQUEST)


# Register Super user for Customers
class RegisterSuperUser(generics.GenericAPIView):
    serializer_class = RegisterSuperUserSerializer

    def post(self, request):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': RegisterSuperUserSerializer(user, context = self.get_serializer_context()).data,
            'token' : AuthToken.objects.create(user)[1]
        })


# Register user for Customers
class RegisterUser(generics.GenericAPIView):
    serializer_class = RegisterUserSerializer

    def post(self, request):
        if not request.user.id:
            return Response("Please Login", status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_superuser:
            return Response("You are not a super user", status=status.HTTP_401_UNAUTHORIZED)
        if not request.data:
            return Response("No content", status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': RegisterUserSerializer(user, context = self.get_serializer_context()).data,
            'token' : AuthToken.objects.create(user)[1]
        })

# User List
class UserList(APIView):

    def get(self,request):
        if not request.user.id:
            return Response("Please Login", status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_superuser:
            return Response("You are not a super user", status=status.HTTP_401_UNAUTHORIZED)
        userDetailsModel = User.objects.all()
        serializer = UserSerializer(userDetailsModel, many=True)
        return Response(serializer.data)


# User List
class TenantList(generics.GenericAPIView):
    # serializer_class = TenantSerializer
    def get(self,request):
        if not request.user.id:
            return Response("Please Login", status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_superuser:
            return Response("You are not a super user", status=status.HTTP_401_UNAUTHORIZED)
        userDetailsModel = Tenant.objects.all()
        serializer = TenantSerializer(userDetailsModel, many=True)
        return Response(serializer.data)