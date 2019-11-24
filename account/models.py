from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self, email, phone, password=None):
        if not email:
            raise ValueError("Users must have email")
        if not phone:
            raise ValueError("Users must have phone")

        user = self.model(
            email = self.normalize_email(email),
            phone = phone,
        )
        user.set_password(password)
        user.save(user = self._db)
        return user
    def create_superuser(self,email, phone, password):
        user = self.model(
            email=self.normalize_email(email),
            phone=phone,
            password = password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using = self._db)
        return user




class Account(AbstractBaseUser):

    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    phone = models.CharField(verbose_name='phone', max_length=60, unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = MyAccountManager()

    def __str__(self):
        return self.email
    def has_perm(self, perm, obj = None):
        return self.is_admin
    def has_module_perms(self, app_label):
        return True
