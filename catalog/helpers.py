from .models import CatalogType
from util import common_methods


def get_all_catalog_types(request):
    return common_methods.get_all_objects(CatalogType, request)