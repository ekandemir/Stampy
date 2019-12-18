from secrets import token_urlsafe
from account.models import BusinessAccount, BusinessToken
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.authtoken.models import Token


def create_business_token(user_email):
    token = token_urlsafe(40)
    user = BusinessAccount.objects.get(email=user_email)
    business_token = BusinessToken(
        token=token,
        business_user=user
    )
    business_token.save()
    return token


def delete_business_token(request):
    token = BusinessToken.objects.get(token=request.META.get("HTTP_AUTHORIZATION")[6:])
    token.delete()


def obtain_business_token(request):
    try:
        user = BusinessAccount.objects.get(email=request.data.get("username"))
        if user.check_password(request.data.get("password")):
            try:
                token = BusinessToken.objects.get(business_user=user)
                return token.token
            except BusinessToken.DoesNotExist:
                return create_business_token(user.email)
        else:
            return None
    except BusinessAccount.DoesNotExist:
        return None


class BusinessAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")  # get the token from header
        if not token:  # no token passed in request headers
            return None  # authentication did not succeed

        try:
            business_token = BusinessToken.objects.get(token=token[6:])
            user = business_token.business_user  # get the user
        except BusinessToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid Token')  # raise exception if user does not exist

        return (user, None)  # authentication successful


class BusinessAdminAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")  # get the token from header
        try:
            if not token:  # no token passed in request headers
                return None  # authentication did not succeed
            else:
                business_token = BusinessToken.objects.get(token=token[6:])
                user = business_token.business_user
                if user.permission == 0:
                    return None
        except BusinessToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')  # raise exception if user does not exist

        return (user, None)  # authentication successful


class UserOrBusinessAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")  # get the token from header

        if not token:  # no token passed in request headers
            return None  # authentication did not succeed

        try:
            user = Token.objects.get(key=token[6:]).user
        except Token.DoesNotExist:
            try:
                user = BusinessToken.objects.get(token=token[6:]).business_user  # get the user
            except BusinessToken.DoesNotExist:
                raise exceptions.AuthenticationFailed('Invalid Token')  # raise exception if user does not exist

        return (user, None)  # authentication successful

