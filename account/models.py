from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import datetime
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


# Create your models here.

# ------- User  -------------
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
            email=self.normalize_email(email),
            phone=phone,
            name=name,
            surname=surname,
            dob=dob,
            gender=gender,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, name, surname, dob, gender, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            phone=phone,
            name=name,
            surname=surname,
            dob=dob,
            gender=gender,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    phone = models.CharField(verbose_name='phone', max_length=60, unique=True)
    name = models.CharField(verbose_name='name', max_length=60, default='name')
    surname = models.CharField(verbose_name='surname', max_length=60, default='surname')
    dob = models.DateField(verbose_name='dob', default=datetime.date(1997, 10, 19))
    gender = models.CharField(verbose_name='gender', max_length=1, default='N')
    date_joined = models.DateTimeField(verbose_name='date_joined', default=datetime.datetime.now())
    last_login = models.DateTimeField(verbose_name='last_login', default=datetime.datetime.now())
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'name', 'surname', 'dob', 'gender']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


# !------! User  !-----------

# -----Business User  ---------
class MyBusinessAccountManager(BaseUserManager):
    def create_user(self, business, email, permission, password=None):
        if not business:
            raise ValueError("Users must have business")
        if not email:
            raise ValueError("Users must have email")
        if not permission:
            raise ValueError("Users must have permission")

        user = self.model(
            business=business,
            email=self.normalize_email(email),
            permission=permission,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class Business(models.Model):
    name = models.CharField(verbose_name='name', max_length=60)
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    card_image = models.CharField(verbose_name='card_image', max_length=60, default='/card')
    stamp_need = models.IntegerField(verbose_name='stamp_need', default=9)
    latitude = models.FloatField(verbose_name="latitude", default=0.0)
    longitude = models.FloatField(verbose_name="longitude", default=0.0)

    def __str__(self):
        return self.name


class BusinessAccount(AbstractBaseUser):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    permission = models.BooleanField(verbose_name='permission', default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["email", 'permission']

    objects = MyBusinessAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def is_admin(self):
        return self.permission

    def has_module_perms(self, app_label):
        return True


class BusinessToken(models.Model):
    token = models.CharField(verbose_name='token', max_length=60)
    business_user = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE)

    def __str__(self):
        return self.token


# !----! Business User !-------

# -----Card ops ---------
class Card(models.Model):
    customer = models.ForeignKey(Account, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    stamp_number = models.IntegerField(verbose_name='stamp_number', default=0)
    stamp_total = models.IntegerField(verbose_name='stamp_total', default=9)
    class Meta:
        unique_together = ('customer', 'business',)


# !----! Card User !-------
class QRCode(models.Model):
    customer = models.ForeignKey(Account, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    qr_code = models.CharField(verbose_name='stamp_number',max_length=36)


# ------ Offers --------
class Offer(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    offer_date = models.DateField(verbose_name='offer_date', default=datetime.date(2019, 12, 30))
    offer_expire_date = models.DateField(verbose_name='offer_expire_date', default=datetime.date(2020, 12, 30))
    offer_body = models.CharField(verbose_name='offer_body',max_length=1000)
    offer_image = models.CharField(verbose_name='offer_body',max_length=1000, default='/image')


# ----- Logs ---------
class StampLog(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    customer = models.ForeignKey(Account, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    operation = models.BooleanField(verbose_name='operation', default=True) # 1 for stamp 0 for free coffee
    date = models.DateTimeField(verbose_name='date', default=datetime.datetime.now())


class AddDeleteCardLog(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    operation = models.BooleanField(verbose_name="operation", default=True)
    date = models.DateTimeField(verbose_name='date', default=datetime.datetime.now())


@receiver(post_save, sender=(settings.AUTH_USER_MODEL or BusinessAccount))
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)













