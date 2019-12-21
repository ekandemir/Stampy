from django.contrib import admin

from account.models import Account,Business,BusinessAccount,BusinessToken,Card,QRCode,Offer,StampLog, AddDeleteCardLog


admin.site.register(Account)
admin.site.register(Business)
admin.site.register(BusinessAccount)
admin.site.register(BusinessToken)
admin.site.register(Card)
admin.site.register(QRCode)
admin.site.register(Offer)
admin.site.register(StampLog)
admin.site.register(AddDeleteCardLog)
# Register your models here.
