import datetime
from rest_framework import serializers,fields

from account.models import Account, Business, BusinessAccount


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    date = fields.DateField(input_formats=['%Y-%m-%d'])
    class Meta:
        model = Account
        fields = ['email', 'phone', 'name', 'surname' ,'gender', 'password', 'password2','date']
        extra_kwargs = {
           'password':{'write_only': True}
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

        # account.dob = datetime.date(int(self.validated_data['dob'][0:4]), int(self.validated_data['dob'][5:7]), int(self.validated_data['dob'][8:10])),
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

    def create(self,validated_data):
        return Business.objects.create(**validated_data)




class BusinessUserRegistrationSerializer(serializers.ModelSerializer):
    business_email = serializers.EmailField()
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model = BusinessAccount
        fields = ['email','business_email', 'permission','password','password2']
        extra_kwargs = {
           'password':{'write_only': True}
        }

    def save(self):
        business = Business.objects.get(email=self.validated_data['business_email'])
        account = BusinessAccount(
            email=self.validated_data['email'],
            business=business,
            permission=0,
        )

        # account.dob = datetime.date(int(self.validated_data['dob'][0:4]), int(self.validated_data['dob'][5:7]), int(self.validated_data['dob'][8:10])),
        password = self.validated_data['password']
        password2 = self.validated_data['password2']


        if password != password2:
            raise serializers.ValidationError({"password": "Passwords must match."})
        account.set_password(password)
        account.save()
        return account




class ChangePasswordSerializer(serializers.Serializer):

	old_password 				= serializers.CharField(style={'input_type':'password'},required=True)
	new_password 				= serializers.CharField(style={'input_type':'password'},required=True)
	confirm_new_password 		= serializers.CharField(style={'input_type':'password'},required=True)