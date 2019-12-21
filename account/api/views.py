from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth import logout, login
from django.contrib.auth.models import AnonymousUser
from django.contrib import messages
from account.api.serializers import (RegistrationSerializer,
                                     ChangePasswordSerializer,
                                     BusinessRegisterSerializer,
                                     BusinessUserRegistrationSerializer,
                                     CardSerializer,
                                     QRCodeSerializer,
                                     OfferSerializer,
                                     StampLogSerializer,
                                     AddDeleteCardSerializer)
from rest_framework.authtoken.models import Token
from account.api.stamp import get_qr_code

from account.api.auth import (create_business_token,
                              delete_business_token,
                              BusinessAuthentication,
                              obtain_business_token,
                              BusinessAdminAuthentication,
                              UserOrBusinessAuthentication)
from account.models import (Account,
                            Business,
                            BusinessToken,
                            BusinessAccount,
                            Card,
                            QRCode,
                            Offer,
                            StampLog,
                            AddDeleteCardLog)

import datetime


@api_view(['POST'])
def registration_view(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['email'] = account.email
            data['phone'] = account.phone
            token = Token.objects.get(user=account).key
            data['token'] = token
            login(request, account)
            return Response({"success": True,
                             "message": "User has been created",
                             "data": data}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False,
                             "message": "Invalid Data",
                             "data": {},
                             "error_code": 0000}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_view(request):
    if not isinstance(request.user, AnonymousUser):
        request.user.auth_token.delete()

        logout(request)

        return Response({"success": True,
                         "message": "Successfully logged out.",
                         "data": {}}, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_password_view(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        return_value, return_data = serializer.update(request.user)
        if return_value:
            return Response({"success": True,
                             "message": "Password successfully changed.",
                             "data": {}},
                            status=status.HTTP_200_OK)
        else:
            return Response({"success": False,
                             "message": return_data,
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"success": False,
                         "message": "Token Not Found",
                         "data": {}},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@authentication_classes([UserOrBusinessAuthentication])
def get_user(request):
    if not isinstance(request.user, AnonymousUser):
        user = request.user
        if isinstance(user, Account):

            data = {"user-type": "customer",
                    "user": {"name": user.name,
                             "surname": user.surname,
                             "email": user.email,
                             "phone": user.phone,
                             "dob": user.dob,
                             "gender": user.gender}}

            return Response({"success": True,
                             "message": "User returned.",
                             "data": data}, status=status.HTTP_200_OK)
        else:
            token = request.META.get("HTTP_AUTHORIZATION")[6:]
            user = BusinessToken.objects.get(token=token).business_user
            if user.permission:
                type = "business_admin"
            else:
                type = "business_cashier"
            data = {"user-type": type,
                    "user": {
                        "business": user.business.name,
                        "email": user.email,
                        "permission": user.permission}}

            return Response({"success": True,
                             "message": "User Returned.",
                             "data": data}, status=status.HTTP_200_OK)
    else:
        return Response({"success": False,
                         "message": "Token Not Found",
                         "data": {}},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def business_registration_view(request):
    if request.user:
        serializer = BusinessRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True,
                             "message": "Business successfully added.",
                             "data": serializer.data}, status=status.HTTP_201_CREATED)

        return Response({"success": False,
                         "message": "Invalid data.",
                         "data": {},
                         "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"success": False,
                         "message": "Token Not Found",
                         "data": {}},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([])
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
                return Response({"success": True,
                                 "message": "Business User has been created",
                                 "data": data}, status=status.HTTP_200_OK)
            else:
                return Response({"success": False,
                                 "message": "Invalid Data",
                                 "data": {},
                                 "error_code": 0000}, status=status.HTTP_400_BAD_REQUEST)


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

    return Response({"success": True,
                     "message": "Successfully logged out.",
                     "data": {}},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
def card_add_view(request):
    if not isinstance(request.user, AnonymousUser):
        token = request.META.get("HTTP_AUTHORIZATION")[6:]
        data = request.data
        data['token'] = token
        serializer = CardSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            log_serializer = AddDeleteCardSerializer(data={"user_id": request.user.id,
                                                           "business_id": request.data.get("business_id"),
                                                           "operation": True})
            if log_serializer.is_valid():
                log_serializer.save()
            return Response({"success": True,
                             "message": "Business User has been created",
                             "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False,
                             "message": "Invalid Data",
                             "data": {},
                             "error_code": 0000}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"success": False,
                         "message": "Token Not Found",
                         "data": {}},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def card_delete_view(request):
    if not isinstance(request.user, AnonymousUser):
        try:
            token = request.META.get("HTTP_AUTHORIZATION")[6:]
            data = request.data
            data['token'] = token
            card = Card.objects.get(customer=Token.objects.get(key=token).user,
                                    business=Business.objects.get(id=request.data.get("business_id")))
            card.delete()
            log_serializer = AddDeleteCardSerializer(data={"user_id": request.user.id,
                                                           "business_id": request.data.get("business_id"),
                                                           "operation": False})
            if log_serializer.is_valid():
                log_serializer.save()

            return Response({"success": True,
                             "message": "Successfully deleted.",
                             "data": {}}, status=status.HTTP_200_OK)
        except Business.DoesNotExist:
            return Response({"success": False,
                             "message": "Business not found.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
        except Card.DoesNotExist:
            return Response({"success": False,
                             "message": "Card not found.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"success": False,
                         "message": "Token Not Found",
                         "data": {}},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def card_list_view(request):
    if not isinstance(request.user, AnonymousUser):
        try:
            token = request.META.get("HTTP_AUTHORIZATION")[6:]
            user = Token.objects.get(key=token).user
            cards = Card.objects.filter(customer=user)
            card_all = Card.objects.all()
            card_data = []
            for card in cards:
                card_data.append({"card_id": card.id,
                                  "card_image": card.business.card_image,
                                  "business_id": card.business.id,
                                  "business_name": card.business.name,
                                  "stamp_number": card.stamp_number,
                                  "stamp_total": card.stamp_total})

            return Response({"success": True,
                             "message": "Successfully returned.",
                             "data": {"cards": card_data}}, status=status.HTTP_200_OK)
        except Business.DoesNotExist:
            return Response({"success": False,
                             "message": "Business not found.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
        except Card.DoesNotExist:
            return Response({"success": False,
                             "message": "Card not found.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"success": False,
                         "message": "Token Not Found",
                         "data": {}},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def business_list_view(request):
    if not isinstance(request.user, AnonymousUser):
        try:
            token = request.META.get("HTTP_AUTHORIZATION")[6:]
            user = Token.objects.get(key=token).user
            businesses = Business.objects.all()
            business_data = []
            cards_owned = [x.business for x in Card.objects.filter(customer=user)]
            for business in businesses:
                business_data.append({"business_name": business.name,
                                      "card_image": business.card_image,
                                      "business_id": business.id,
                                      "is_owned": business in cards_owned})

            return Response({"success": True,
                             "message": "Successfully returned.",
                             "data": {"businesses": business_data}},
                            status=status.HTTP_200_OK)
        except Business.DoesNotExist:
            return Response({"success": False,
                             "message": "Business not found.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
        except Card.DoesNotExist:
            return Response({"success": False,
                             "message": "Card not found.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"success": False,
                         "message": "Token Not Found",
                         "data": {}},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def get_qr_view(request):
    if not isinstance(request.user, AnonymousUser):
        try:
            data = request.data
            data["customer_id"] = request.user.id
            data["business_id"] = request.data.get("business_id")
            data["qr_code"] = get_qr_code()

            serializer = QRCodeSerializer(data=data)
            if serializer.is_valid():
                qr_code = serializer.save()
                return Response({"success": True,
                                 "message": "QR Code successfully created.",
                                 "data": {"qr_code": qr_code.qr_code}}, status=status.HTTP_201_CREATED)

            return Response({"success": False,
                             "message": "Data is not valid.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
        except Business.DoesNotExist:
            return Response({"success": False,
                             "message": "Business not found.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"success": False,
                         "message": "Token Not Found",
                         "data": {}},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([BusinessAuthentication])
def validate_qr_view(request):
    if not isinstance(request.user, AnonymousUser):
        try:
            token = request.META.get("HTTP_AUTHORIZATION")[6:]
            business = BusinessToken.objects.get(token=token)
            qr_code = QRCode.objects.get(qr_code=request.data.get("qr_code"))
            if qr_code.business.id == business.id:
                cards = Card.objects.filter(customer=qr_code.customer).filter(business=qr_code.business)
                if len(cards) == 1 and cards[0].stamp_number < cards[0].stamp_total:
                    cards[0].stamp_number += 1
                    cards[0].save()
                    qr_code.delete()
                    log_serializer = StampLogSerializer(data={"card_id": cards[0].id,
                                                              "operation": True})
                    if log_serializer.is_valid():
                        log_serializer.save()
                    return Response({"success": True,
                                     "message": "Successfully stamped.",
                                     "data": {}},
                                    status=status.HTTP_200_OK)
                else:
                    cards[0].stamp_number -= cards[0].stamp_total
                    cards[0].save()
                    qr_code.delete()
                    log_serializer = StampLogSerializer(data={"card_id": cards[0].id,
                                                              "operation": False})
                    if log_serializer.is_valid():
                        log_serializer.save()
                    return Response({"success": True,
                                     "message": "Free coffee successfully given.",
                                     "data": {}},
                                    status=status.HTTP_200_OK)
            return Response({"success": False,
                             "message": "Data is invalid.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
        except QRCode.DoesNotExist:
            return Response({"success": False,

                             "message": "QRCode is invalid.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
        except Business.DoesNotExist:
            return Response({"success": False,

                             "message": "Business not found.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
        except Card.DoesNotExist:
            return Response({"success": False,
                             "message": "Card not found.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"success": False,
                         "message": "Token Not Found",
                         "data": {}},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def business_list_location(request):
    if not isinstance(request.user, AnonymousUser):
        try:
            longitude = request.data.get("longitude")
            latitude = request.data.get("latitude")
            distance = request.data.get("distance")
            businesses = Business.objects.filter(longitude__lte=longitude + distance).filter(
                longitude__gte=longitude - distance). \
                filter(latitude__lte=latitude + distance).filter(latitude__gte=latitude - distance)
            business_data = []
            for business in businesses:
                business_data.append({"business_name": business.name,
                                      "business_email": business.email,
                                      "latitude": business.latitude,
                                      "longitude": business.longitude})
            return Response({"success": True,
                             "message": "Successfully returned.",
                             "data": {"businesses": business_data}}, status=status.HTTP_200_OK)
        except Business.DoesNotExist:
            return Response({"success": False,
                             "message": "Business not found.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"success": False,
                         "message": "Token Not Found",
                         "data": {}},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([BusinessAuthentication])
def offer_add_view(request):
    if not isinstance(request.user, AnonymousUser):
        token = request.META.get("HTTP_AUTHORIZATION")[6:]
        business = BusinessToken.objects.get(token=token).business_user
        data = request.data
        data['business_id'] = business.id
        serializer = OfferSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True,
                             "message": "Business User has been created",
                             "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False,
                             "message": "Invalid Data",
                             "data": {},
                             "error_code": 0000}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"success": False,
                         "message": "Token Not Found",
                         "data": {}},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def offer_list_view(request):
    if not isinstance(request.user, AnonymousUser):
        try:
            token = request.META.get("HTTP_AUTHORIZATION")[6:]
            user = Token.objects.get(key=token).user
            offers = Offer.objects.all()
            offer_data = []
            for offer in offers:
                offer_data.append({"business_id": offer.business.id,
                                   "offer_date": offer.offer_date,
                                   "offer_expire_date": offer.offer_expire_date,
                                   "offer_body": offer.offer_body})

            return Response({"success": True,
                             "message": "Successfully returned.",
                             "data": {"offers": offer_data}},
                            status=status.HTTP_200_OK)
        except Offer.DoesNotExist:
            return Response({"success": False,
                             "message": "Offer not found.",
                             "data": {},
                             "error": 0000}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"success": False,
                         "message": "Token Not Found",
                         "data": {}},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@authentication_classes([BusinessAdminAuthentication])
def insights_view(request):
    if not isinstance(request.user, AnonymousUser):
        business = request.user.business
        data = {}
        data['total_coffee'] = len(StampLog.objects.filter(business=business))
        data['total_coffee_month'] = len(
            StampLog.objects.filter(business=business).filter(
            date__gte=datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().days)))
        data['total_free_coffee'] = len(StampLog.objects.filter(business=business).filter(operation=False))
        data['total_free_coffee'] = len(StampLog.objects.filter(business=business).filter(operation=False).filter(
            date__gte=datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().days)))
        data['age_distribution'] = [0, 0, 0, 0, 0]
        data['gender_distribution'] = [0, 0, 0]
        customers = [x for x in Card.objects.all(business=business).customer]
        for customer in customers:
            if (datetime.datetime.now() - customer.dob).year < 18:
                data['age_distribution'][0] += 1
            elif (datetime.datetime.now() - customer.dob).year < 24:
                data['age_distribution'][1] += 1
            elif (datetime.datetime.now() - customer.dob).year < 35:
                data['age_distribution'][2] += 1
            elif (datetime.datetime.now() - customer.dob).year < 45:
                data['age_distribution'][3] += 1
            else:
                data['age_distribution'][4] += 1

            if customer.gender == 'F':
                data['gender_distribution'][0] += 1
            elif customer.gender == 'M':
                data['gender_distribution'][1] += 1
            else:
                data['gender_distribution'][2] += 1

        return Response({"success": True,
                         "message": "Insights returned.",
                         "data": data},
                        status=status.HTTP_200_OK)
    else:
        return Response({"success": False,
                         "message": "Token Not Found",
                         "data": {}},
                        status=status.HTTP_401_UNAUTHORIZED)
