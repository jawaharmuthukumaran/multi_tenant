from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from .models import Tenant,Domain
from django.contrib.auth.models import User


# Serializer for creating domain for the new tenant
class RegisterDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = '__all__'


# Serializer for Creating a new Tenant
class RegisterCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'


# Tenant Serializer
class TenantSerializer(serializers.ModelSerializer):
    domains = RegisterDomainSerializer(read_only = True, many = True)
    class Meta:
        model = Tenant
        fields = '__all__'    


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password' : {'write_only' : True}}


# Serializer for creaitng superuser for a tenant
class RegisterSuperUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password' : {'write_only' : True}}

    def create(self, validated_data):
        user = User.objects.create_superuser(validated_data['username'], validated_data['email'], validated_data['password'])
        return user


# Serializer for creating user for a tenant
class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password' : {'write_only' : True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        return user


# Change Password
class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)