from django.views.decorators.http import require_POST
from django.http import JsonResponse
from core.services.imports import import_users_from_csv, import_print_events_from_json
import json

@require_POST
def import_users_api_view(request):
    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "Файл не передан"}, status=400)

    if not file.name.endswith(".csv"):
        return JsonResponse({"error": "Ожидается CSV-файл"}, status=400)

    result = import_users_from_csv(file)
    return JsonResponse(result)

@require_POST
def import_print_events_api_view(request):
    try:
        events = json.loads(request.body.decode('utf-8'))
        if not isinstance(events, list):
            return JsonResponse({"error": "Invalid format. Expected list of events"}, status=400)

        result = import_print_events_from_json(events)
        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
