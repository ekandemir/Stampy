from django.shortcuts import render
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from . import helpers
from django.http import HttpResponse


# Create your views here.
# Create your views here.
@csrf_exempt
@api_view(['POST'])
def catalog_type(request):
    print(">>>",request.data)
    return HttpResponse(str(request.data['a'][0]))
    # return helpers.get_all_catalog_types(request)