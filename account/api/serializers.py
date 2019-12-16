import datetime
from abc import ABC

from rest_framework import serializers, fields

from account.models import Account, Business, BusinessAccount, Card, BusinessToken, QRCode
from rest_framework.authtoken.models import Token


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    date = fields.DateField(input_formats=['%Y-%m-%d'])

    class Meta:
        model = Account
        fields = ['email', 'phone', 'name', 'surname', 'gender', 'password', 'password2', 'date']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        account = Account(
            email=self.validated_data['email'],
            phone=self.validated_data['phone'],
            name=self.validated_data['name'],
            surname=self.validated_data['surname'],
            dob=self.validated_data['date'],
            gender=self.validated_data['gender'],
        )

        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if int(account.phone) < 5000000000 or int(account.phone) > 5999999999:
            raise serializers.ValidationError({"name": "Phone is not proper."})

        if password != password2:
            raise serializers.ValidationError({"password": "Passwords must match."})
        account.set_password(password)
        account.save()
        return account


class BusinessRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, allow_blank=False, max_length=100)
    email = serializers.EmailField(required=True, allow_blank=False)
    card_image = serializers.CharField(required=True, allow_blank=False, max_length=100)
    stamp_need = serializers.IntegerField(required=True)

    def create(self, validated_data):
        return Business.objects.create(**validated_data)


class BusinessUserRegistrationSerializer(serializers.ModelSerializer):
    business_email = serializers.EmailField()
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = BusinessAccount
        fields = ['email', 'business_email', 'permission', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        business = Business.objects.get(email=self.validated_data['business_email'])
        account = BusinessAccount(
            email=self.validated_data['email'],
            business=business,
            permission=0,
        )

        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({"password": "Passwords must match."})
        account.set_password(password)
        account.save()
        return account


class CardSerializer(serializers.Serializer):
    business_id = serializers.CharField(required=True, allow_blank=False, max_length=100)
    stamp_number = serializers.IntegerField(default=0)
    stamp_total = serializers.IntegerField(default=9)
    token = serializers.CharField(required=True, allow_blank=False, max_length=100)

    def save(self):
        customer = Token.objects.get(key=self.validated_data['token']).user
        business = Business.objects.get(id=self.validated_data['business_id'])
        card = Card(customer=customer,
                    business=business,
                    stamp_number=0,
                    stamp_total=business.stamp_need)

        card.save()
        return card

    def create(self, validated_data):
        return Card.objects.create(**validated_data)


class QRCodeSerializer(serializers.Serializer):
    business_id = serializers.CharField(required=True, allow_blank=False, max_length=100)
    customer_id = serializers.CharField(required=True, allow_blank=False, max_length=100)
    qr_code = serializers.CharField(required=True, allow_blank=False, max_length=36)

    def save(self):
        customer = Account.objects.get(id=self.validated_data['customer_id'])
        business = Business.objects.get(id=self.validated_data['business_id'])
        qr_code = QRCode(customer=customer,
                    business=business,
                    qr_code=self.validated_data['qr_code'])

        qr_code.save()
        return qr_code

    def create(self, validated_data):
        return QRCode.objects.create(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={'input_type': 'password'}, required=True)
    password1 = serializers.CharField(style={'input_type': 'password'}, required=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, required=True)

    def update(self, user):
        if self.validated_data["password1"] == self.validated_data["password2"]:
            user.set_password(self.validated_data["password2"])
            user.save()
            return user
        else:
            return None
