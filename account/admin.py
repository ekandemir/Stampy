from django.contrib import admin

from account.models import Account,Business,BusinessAccount,BusinessToken,Card,QRCode,Offer


admin.site.register(Account)
admin.site.register(Business)
admin.site.register(BusinessAccount)
admin.site.register(BusinessToken)
admin.site.register(Card)
admin.site.register(QRCode)
admin.site.register(Offer)
# Register your models here.
