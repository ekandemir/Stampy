from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth import logout,login
from django.contrib import messages
from account.api.serializers import RegistrationSerializer,ChangePasswordSerializer, BusinessRegisterSerializer, BusinessUserRegistrationSerializer
from rest_framework.authtoken.models import Token

from account.api.auth import (create_business_token,
                              delete_business_token,
                              BusinessAuthentication,
                              obtain_business_token)


@api_view(['POST'])
def registration_view(request):

    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = "Successfully registered new user."
            data['email'] = account.email
            data['phone'] = account.phone
            token = Token.objects.get(user=account).key
            data['token'] = token
            login(request,account)
        else:
            data = serializer.errors
        return Response(data)


@api_view(['POST'])
def logout_view(request):
    request.user.auth_token.delete()


    logout(request)

    return Response({"success": "Successfully logged out."},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
def business_registration_view(request):
    serializer = BusinessRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def business_user_registration_view(request):

    if request.method == 'POST':
        serializer = BusinessUserRegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = "Successfully registered new user."
            data['email'] = account.email
            token = create_business_token(user_email=account.email)
            data['token'] = token
        else:
            data = serializer.errors
        return Response(data)


@api_view(['POST'])
def business_user_login_view(request):

    if request.method == 'POST':
        token = obtain_business_token(request)
        if  token:
            return Response({"token": token},
                            status=status.HTTP_200_OK)
        else:
            return Response({"non_field_errors": ["Unable to log in with provided credentials."]},
                            status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([BusinessAuthentication])
def business_logout_view(request):
    delete_business_token(request)

    return Response({"success": "Successfully logged out."},
                    status=status.HTTP_200_OK)
