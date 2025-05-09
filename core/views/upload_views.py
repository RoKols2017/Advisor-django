from django.shortcuts import render, redirect
from django.contrib import messages
from core.services.imports import import_users_from_csv, import_print_events_from_json
import json

def upload_view(request):
    if request.method == "POST":
        ftype = request.POST.get("type")
        file = request.FILES.get("file")

        if not file:
            messages.error(request, "❌ Файл не выбран")
            return redirect("upload")

        try:
            if ftype == "users" and file.name.endswith(".csv"):
                result = import_users_from_csv(file)

            elif ftype == "events" and file.name.endswith(".json"):
                data = file.read().decode("utf-8-sig")
                events = json.loads(data)
                result = import_print_events_from_json(events)

            else:
                messages.error(request, "❌ Неверный формат файла")
                return redirect("upload")

            messages.success(request, f"✅ Импортировано: {result['created']}")

            if result["errors"]:
                messages.warning(request, f"⚠️ Ошибки: {len(result['errors'])}")
                for err in result["errors"][:5]:
                    messages.error(request, f"❌ {err}")

        except Exception as ex:
            messages.error(request, f"💥 Неожиданная ошибка: {str(ex)}")

        return redirect("upload")

    return render(request, "core/upload.html")
