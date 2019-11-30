from django.conf.urls import url
from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from .views import CreateUserAPIView, LogoutUserAPIView

# urlpatterns = [
#     path('register', views.register, name='register'),
# ]

urlpatterns = [
    path('login',
        obtain_auth_token,
        name='auth_user_login'),
    path('register',
        CreateUserAPIView.as_view(),
        name='auth_user_create'),
    path('logout',
        LogoutUserAPIView.as_view(),
        name='auth_user_logout')
]
