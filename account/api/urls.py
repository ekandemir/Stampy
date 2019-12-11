from django.urls import path
from account.api.views import (
    registration_view,
    logout_view,
    business_registration_view,
    business_user_registration_view,
    business_logout_view,
    business_user_login_view
)
from rest_framework.authtoken.views import obtain_auth_token
app_name = 'account'

urlpatterns = [
    path('register', registration_view, name='register'),
    path('login', obtain_auth_token, name='login'),
    path('login_business', business_user_login_view, name='login_business'),
    path('logout', logout_view, name='logout'),
    path('logout_business', business_logout_view, name='logout_business'),
    path('register_business', business_registration_view, name='business_register'),
    path('business_user_register', business_user_registration_view, name='business_user_register'),
    #path('change_password', change_password_view.as_view(), name="change_password"),

]