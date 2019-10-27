import json
import traceback
from django.http import JsonResponse
from . import log

logger = log.getLogger(__name__)


def response(msg, status, safe=True):
    return JsonResponse(
        msg, safe=safe, json_dumps_params={'indent': 2}, status=status)


def update_dict(obj):
    obj_dict = obj.__dict__.copy()
    obj_dict.pop('_state')
    return obj_dict


def get_all_objects(model_name, request):
    try:
        page_size = request.GET.get('page_size')
        page_num = request.GET.get('page_num')

        page_size = min(5000, int(page_size)) if page_size else 100
        page_num = int(page_num) if page_num else 1

        start = page_size * (page_num - 1)
        end = start + page_size

        objects = model_name.objects.all()[start:end]
        obj_list = []
        for obj in objects:
            obj_list.append(update_dict(obj))
        return response(obj_list, safe=False, status=200)
    except ValueError as e:
        msg = {"error": str(e)}
        return response(msg, status=400)
    except:
        error_message = "Internal Server Error."
        logger.error({
            'message': error_message,
            'error': traceback.format_exc()
        })
        return response({"error": error_message}, status=500)