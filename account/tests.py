from django.test import TestCase
from account.models import (Account,
                            Business,
                            BusinessToken,
                            BusinessAccount,
                            Card,
                            QRCode,
                            Offer,
                            StampLog,
                            AddDeleteCardLog)
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import json


# Create your tests here.
class TestAccount(TestCase):
    def setUp(self):
        self.test_account = Account.objects.create_user(email="test@email.com",
                                                   phone="5535535353",
                                                   name="test",
                                                   surname="testson",
                                                   password="123",
                                                   dob="2019-9-11",
                                                   gender="E")
        self.test_account2 = Account.objects.create_user(email="test2@email.com",
                                                   phone="5535535352",
                                                   name="test2",
                                                   surname="testson2",
                                                   password="123",
                                                   dob="2019-9-12",
                                                   gender="E")
        self.business = Business.objects.create(name="test_business",
                                                email='test@business.com',
                                                card_image='test.com/business.jpg',
                                                stamp_need=9,
                                                latitude=40.5,
                                                longitude=40.5)

        self.business_admin = BusinessAccount.objects.create_user(business=self.business,
                                                                  email="admin@business.com",
                                                                  permission=True,
                                                                  password="123")

        self.business_cashier = BusinessAccount.objects.create_user(business=self.business,
                                                                    email="cashier@business.com",
                                                                    permission=True,
                                                                    password="123")
        self.business_cashier.permission = False


    # User Tests

    def test_user_login(self):
        response = self.client.post('/api/login', {"username": self.test_account.email,
                                                   "password": "123"})

        self.assertEqual(response.status_code, 200)

    def test_user_get_user(self):
        token = Token.objects.get(user_id=self.test_account.id)
        client = APIClient()
        client.force_login(self.test_account)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.get('/api/get-user')

        self.assertEqual(response.status_code, 200)

    def test_user_logout(self):
        token = Token.objects.get(user_id=self.test_account.id)
        client = APIClient()
        client.force_login(self.test_account)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post('/api/logout')

        self.assertEqual(response.status_code, 200)

    def test_user_register(self):
        response = self.client.post('/api/register',  {"email": "teste@email.com",
                                                       "phone": "5535535350",
                                                       "name": "test",
                                                       "surname": "testson",
                                                       "password": "123",
                                                       "password2": "123",
                                                       "date": "2019-9-11",
                                                       "gender": "E"})

        self.assertEqual(response.status_code, 200)

    def test_user_list_offer(self):
        token = Token.objects.get(user_id=self.test_account.id)
        client = APIClient()
        client.force_login(self.test_account)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.get('/api/offer-list')

        self.assertEqual(response.status_code, 200)

    def test_user_list_business(self):
        token = Token.objects.get(user_id=self.test_account.id)
        client = APIClient()
        client.force_login(self.test_account)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.get('/api/business-list')

        self.assertEqual(response.status_code, 200)

    def test_user_list_business_locations(self):
        token = Token.objects.get(user_id=self.test_account.id)
        client = APIClient()
        client.force_login(self.test_account)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post('/api/business-list-location',
                               json.dumps({"longitude": 29.110,
                                           "latitude": 41.111,
                                           "distance": 100}),
                               content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_user_get_qr(self):
        token = Token.objects.get(user_id=self.test_account.id)
        client = APIClient()
        client.force_login(self.test_account)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post('/api/get-qr',
                               json.dumps({"business_id": self.business.id}),
                               content_type='application/json')

        self.assertEqual(response.status_code, 201)

    def test_user_change_password(self):
        token = Token.objects.get(user_id=self.test_account.id)
        client = APIClient()
        client.force_login(self.test_account)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post('/api/change-password',
                               json.dumps({"password1": "123",
                                           "password2": "123",
                                           "old_password": "123"}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # User Card Tests

    def test_user_card_add(self):
        token = Token.objects.get(user_id=self.test_account.id)
        client = APIClient()
        client.force_login(self.test_account)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post('/api/card-add',
                               json.dumps({"business_id": self.business.id}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_user_card_delete(self):
        token = Token.objects.get(user_id=self.test_account.id)
        client = APIClient()
        client.force_login(self.test_account)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.post('/api/card-add',
                               json.dumps({"business_id": self.business.id}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = client.post('/api/card-delete',
                               json.dumps({"business_id": self.business.id}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_user_list_cards(self):
        token = Token.objects.get(user_id=self.test_account.id)
        client = APIClient()
        client.force_login(self.test_account)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.get('/api/card-list')

        self.assertEqual(response.status_code, 200)


    # Admin Tests

    def test_admin_created(self):
        self.assertEqual(self.business_admin.email, "admin@business.com")

    def test_admin_login(self):
        response = self.client.post('/api/login-business', {"username": self.business_cashier.email,
                                                            "password": "123"})
        self.assertEqual(response.status_code, 200)

    def test_admin_logout(self):
        response = self.client.post('/api/login-business', {"username": self.business_admin.email,
                                                            "password": "123"})
        token = BusinessToken.objects.get(business_user__email=self.business_admin.email)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.token)
        response = client.post('/api/logout-business')
        self.assertEqual(response.status_code, 200)

    def test_admin_getuser(self):
        response = self.client.post('/api/login-business', {"username": self.business_admin.email,
                                                            "password": "123"})
        token = BusinessToken.objects.get(business_user__email=self.business_admin.email)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.token)
        response = client.get('/api/get-user')
        self.assertEqual(response.data['data']['user-type'], "business_admin")

    def test_admin_unauth(self):
        response = self.client.post('/api/login-business', {"username": self.business_admin.email,
                                                            "password": "456"})
        self.assertEqual(response.status_code, 401)

    # Business User Tests

    def test_business_user(self):
        self.assertEqual(self.business_admin.business, self.business)

    def test_business_user_register(self):
        response = self.client.post('/api/business-user-register', {"business_email": "test@business.com",
                                                               "password": "123",
                                                               "password2": "123",
                                                               "email": "testadmin@business.com"})
        self.assertEqual(response.status_code, 200)

    def test_business_user_register_pw_different(self):
        response = self.client.post('/api/business-user-register', {"business_email":"test@business.com",
                                                               "password":"123",
                                                               "password2":"124",
                                                               "email":"testadmin@business.com"})
        self.assertEqual(response.status_code, 400)

    def test_business_user_register_email_missing(self):
        response = self.client.post('/api/business-user-register', {"business_email":"test@business.com",
                                                               "password": "123",
                                                               "password2": "123",})
        self.assertEqual(response.status_code, 400)

    def test_business_user_register_business_email_missing(self):
        response = self.client.post('/api/business-user-register', {"password":"123",
                                                               "password2":"123",
                                                               "email":"testadmin@business.com"})
        self.assertEqual(response.status_code, 400)

    def test_business_user_validate_qr(self):
        response2 = self.client.post('/api/login-business', {"username": self.business_cashier.email,
                                                             "password": "123"})
        token_user = Token.objects.get(user_id=self.test_account.id)
        client1 = APIClient()
        client1.force_login(self.test_account)
        client1.credentials(HTTP_AUTHORIZATION='Token ' + token_user.key)
        response1 = client1.post('/api/get-qr',
                               json.dumps({"business_id": self.business_cashier.business_id}),
                               content_type='application/json')

        token = BusinessToken.objects.get(business_user__email=self.business_cashier.email)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.token)
        response = client.post('/api/validate-qr',
                               json.dumps({"qr_code": response1.data["data"]["qr_code"]}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)


    # Business Admin Tests

    def test_business_admin_permission(self):
        self.assertEqual(self.business_admin.permission, True)

    def test_business_admin_insights(self):
        response = self.client.post('/api/login-business', {"username": self.business_admin.email,
                                                            "password": "123"})
        token = BusinessToken.objects.get(business_user__email=self.business_admin.email)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.token)
        response = client.get('/api/insights')
        self.assertEqual(response.status_code, 200)

    def test_business_cashier_permission(self):
        self.assertEqual(self.business_cashier.permission, False)

    def test_business(self):
        self.assertEqual(self.business.name, "test_business")

    # Business Cashier Tests

    def test_cashier_login(self):
        response = self.client.post('/api/login-business', {"username": self.business_cashier.email,
                                                            "password": "123"})
        self.assertEqual(response.status_code, 200)

    def test_cashier_unauth(self):
        response = self.client.post('/api/login-business', {"username": self.business_cashier.email,
                                                            "password": "456"})
        self.assertEqual(response.status_code, 401)

    def test_cashier_logout(self):
        response = self.client.post('/api/login-business', {"username": self.business_cashier.email,
                                                            "password": "123"})
        token = BusinessToken.objects.get(business_user__email=self.business_cashier.email)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.token)
        response = client.post('/api/logout-business')
        self.assertEqual(response.status_code, 200)

    def test_cashier_created(self):
        self.assertEqual(self.business_cashier.email, "cashier@business.com")




















