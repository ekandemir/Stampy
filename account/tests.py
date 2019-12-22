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

# Create your tests here.
class TestAccount(TestCase):
    def setUp(self):
        self.account = Account.objects.create_user(email="deneme@email.com",
                                                   phone="5535535353",
                                                   name="deneme",
                                                   surname="denemeoglu",
                                                   password="123",
                                                   dob="2019-9-11",
                                                   gender="E")
    def test_username(self):
        self.assertEqual(self.account.name, "deneme")