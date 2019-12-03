from django.urls import path
from account.api.views import (
    registration_view,
    logout_view,
)
from rest_framework.authtoken.views import obtain_auth_token
app_name = 'account'

urlpatterns = [
    path('register', registration_view, name='register'),
    path('login', obtain_auth_token, name='login'),
    path('logout', logout_view, name='logout'),
    #path('change_password', change_password_view.as_view(), name="change_password"),

]