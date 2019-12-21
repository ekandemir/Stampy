from django.urls import path
from account.api.views import (
    registration_view,
    logout_view,
    business_registration_view,
    business_user_registration_view,
    business_logout_view,
    business_user_login_view,
    card_add_view,
    card_delete_view,
    card_list_view,
    business_list_view,
    get_qr_view,
    validate_qr_view,
    change_password_view,
    business_list_location,
    offer_add_view,
    offer_list_view,
    get_user,
    insights_view)

from rest_framework.authtoken.views import obtain_auth_token

app_name = 'account'

urlpatterns = [
    path('register', registration_view, name='register'),
    path('login', obtain_auth_token, name='login'),
    path('login-business', business_user_login_view, name='login_business'),
    path('logout', logout_view, name='logout'),
    path('logout-business', business_logout_view, name='logout_business'),
    path('register-business', business_registration_view, name='business_register'),
    path('business-user-register', business_user_registration_view, name='business_user_register'),
    path('change-password', change_password_view, name="change_password"),
    path('get-user',get_user, name="get_user"),

    path('card-add', card_add_view, name='card_add_view'),
    path('card-delete', card_delete_view, name='card_delete_view'),
    path('card-list', card_list_view, name='card_list_view'),
    path('business-list', business_list_view, name='business_list_view'),
    path('business-list-location', business_list_location, name='business_list_location_view'),


    path('get-qr', get_qr_view, name='get_qr_view'),
    path('validate-qr', validate_qr_view, name='get_qr_view'),


    path('offer-add', offer_add_view, name='offer_add_view'),
    path('offer-list', offer_list_view, name='offer_list_view'),

    path('insights', insights_view, name='insights')



]
