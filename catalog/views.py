from django.shortcuts import render
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from . import helpers

# Create your views here.
# Create your views here.
@csrf_exempt
@api_view(['GET'])
def catalog_type(request):
    return helpers.get_all_catalog_types(request)