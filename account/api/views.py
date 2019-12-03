from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import logout,login
from django.contrib import messages
from account.api.serializers import RegistrationSerializer,ChangePasswordSerializer
from rest_framework.authtoken.models import Token


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

    return Response({"success": ("Successfully logged out.")},
                    status=status.HTTP_200_OK)