from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth import logout, login
from django.contrib import messages
from account.api.serializers import (RegistrationSerializer,
                                     ChangePasswordSerializer,
                                     BusinessRegisterSerializer,
                                     BusinessUserRegistrationSerializer,
                                     CardSerializer,
                                     QRCodeSerializer)
from rest_framework.authtoken.models import Token
from account.api.stamp import get_qr_code

from account.api.auth import (create_business_token,
                              delete_business_token,
                              BusinessAuthentication,
                              obtain_business_token)
from account.models import (Account,
                            Business,
                            BusinessToken,
                            BusinessAccount,
                            Card,
                            QRCode)


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
            login(request, account)
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
def change_password_view(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        a , b = serializer.update(request.user)
        if a:
            return Response({"success": "Password successfully changed."},
                        status=status.HTTP_200_OK)
        else:
            return Response(b, status=status.HTTP_400_BAD_REQUEST)



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
@authentication_classes([])
@permission_classes([])
def business_user_login_view(request):
    if request.method == 'POST':
        token = obtain_business_token(request)
        if token:
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


@api_view(['POST'])
def card_add_view(request):
    token = request.META.get("HTTP_AUTHORIZATION")[6:]
    data = request.data
    data['token'] = token
    serializer = CardSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def card_delete_view(request):
    try:
        token = request.META.get("HTTP_AUTHORIZATION")[6:]
        data = request.data
        data['token'] = token
        card = Card.objects.get(customer=Token.objects.get(key=token).user,
                                business=Business.objects.get(id=request.data.get("business_id")))
        card.delete()

        return Response({"success": "Successfully deleted."},
                        status=status.HTTP_200_OK)
    except Business.DoesNotExist:
        return Response({"success": ""}, status=status.HTTP_400_BAD_REQUEST)
    except Card.DoesNotExist:
        return Response({"success": ""}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def card_list_view(request):
    try:
        token = request.META.get("HTTP_AUTHORIZATION")[6:]
        data = request.data
        data['token'] = token
        user = Token.objects.get(key=token).user
        cards = Card.objects.filter(customer=user)
        card_all = Card.objects.all()
        card_data = []
        for card in cards:
            card_data.append({"card_id": card.id,
                              "card_image": card.business.card_image,
                              "business_id": card.business.id})

        return Response({"success": "Successfully returned.", "cards": card_data},
                        status=status.HTTP_200_OK)
    except Business.DoesNotExist:
        return Response({"success": ""}, status=status.HTTP_400_BAD_REQUEST)
    except Card.DoesNotExist:
        return Response({"success": ""}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def business_list_view(request):
    try:
        token = request.META.get("HTTP_AUTHORIZATION")[6:]
        data = request.data
        data['token'] = token
        user = Token.objects.get(key=token).user
        businesses = Business.objects.all()
        business_data = []
        cards_owned = [x.business for x in Card.objects.filter(customer=user)]
        for business in businesses:
            business_data.append({"business_name": business.name,
                                  "card_image": business.card_image,
                                  "business_id": business.id,
                                  "is_owned": business in cards_owned})

        return Response({"success": "Successfully returned.", "businesses": business_data},
                        status=status.HTTP_200_OK)
    except Business.DoesNotExist:
        return Response({"success": ""}, status=status.HTTP_400_BAD_REQUEST)
    except Card.DoesNotExist:
        return Response({"success": ""}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_qr_view(request):
    try:
        token = request.META.get("HTTP_AUTHORIZATION")[6:]
        user = Token.objects.get(key=token).user
        data = request.data
        data["customer_id"] = user.id
        data["business_id"] = request.data.get("business_id")
        data["qr_code"] = get_qr_code()

        serializer = QRCodeSerializer(data=data)
        if serializer.is_valid():
            qr_code = serializer.save()
            return Response({"qr_code": qr_code.qr_code}, status=status.HTTP_201_CREATED)
        return Response({"qr_code": ""}, status=status.HTTP_201_CREATED)
    except Business.DoesNotExist:
        return Response({"success": ""}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([BusinessAuthentication])
def validate_qr_view(request):
    try:
        token = request.META.get("HTTP_AUTHORIZATION")[6:]
        business = BusinessToken.objects.get(token=token).business_user
        qr_code = QRCode.objects.get(qr_code=request.data.get("qr_code"))
        if qr_code.business.id == business.id:
            cards = Card.objects.filter(customer=qr_code.customer).filter(business=qr_code.business)
            if len(cards) == 1:
                cards[0].stamp_number += 1
                cards[0].save()

            return Response({"success": "Successfully stamped."},
                        status=status.HTTP_200_OK)
        return Response({"success": ""}, status=status.HTTP_400_BAD_REQUEST)
    except Business.DoesNotExist:
        return Response({"success": ""}, status=status.HTTP_400_BAD_REQUEST)
    except Card.DoesNotExist:
        return Response({"success": ""}, status=status.HTTP_400_BAD_REQUEST)

