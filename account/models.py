from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import datetime
# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self, email, phone, name, surname, dob, gender, password=None):
        if not email:
            raise ValueError("Users must have email")
        if not phone:
            raise ValueError("Users must have phone")
        if not name:
            raise ValueError("Users must have name")
        if not surname:
            raise ValueError("Users must have surname")
        if not dob:
            raise ValueError("Users must have surname")
        if not gender:
            raise ValueError("Users must have surname")

        user = self.model(
            email = self.normalize_email(email),
            phone = phone,
            name = name,
            surname = surname,
            dob = dob,
            gender = gender,
        )
        user.set_password(password)
        user.save(using = self._db)
        return user
    def create_superuser(self,email, password):
        user = self.create_user(
            email=self.normalize_email(email),
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
    name = models.CharField(verbose_name='name', max_length=60, default='name')
    surname = models.CharField(verbose_name='surname', max_length=60, default='surname')
    dob = models.DateField(verbose_name= 'dob',default=datetime.date(1997, 10, 19))
    gender = models.CharField(verbose_name='gender', max_length=1, default='N')
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'name', 'surname', 'dob', 'gender']

    objects = MyAccountManager()

    def __str__(self):
        return self.email
    def has_perm(self, perm, obj = None):
        return self.is_admin
    def has_module_perms(self, app_label):
        return True
