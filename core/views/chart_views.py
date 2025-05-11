from django.shortcuts import render
from core.models import PrintEvent
from datetime import datetime, timedelta
from calendar import monthrange
from django.db.models import Sum
from django.utils.timezone import make_aware

def print_chart_view(request):
    # 1. Получаем текущий месяц
    month_param = request.GET.get("month")
    try:
        current_month = datetime.strptime(month_param, "%Y-%m") if month_param else datetime.today().replace(day=1)
    except ValueError:
        current_month = datetime.today().replace(day=1)

    year = current_month.year
    month = current_month.month
    start_date = make_aware(datetime(year, month, 1))
    end_date = make_aware(datetime(year, month, monthrange(year, month)[1], 23, 59, 59))

    # 2. Считаем кол-во страниц по отделам
    events = PrintEvent.objects.filter(timestamp__range=(start_date, end_date)).select_related("printer__department")
    stats = {}

    for event in events:
        dept = event.printer.department
        key = f"{dept.code} — {dept.name}"
        stats[key] = stats.get(key, 0) + event.pages

    # 3. Подготовка данных
    labels = list(stats.keys())
    values = list(stats.values())

    # 4. Предыдущий и следующий месяц
    prev_month = (start_date - timedelta(days=1)).replace(day=1)
    next_month = (start_date + timedelta(days=32)).replace(day=1)

    return render(request, "core/print_chart.html", {
        "labels": labels,
        "values": values,
        "current_month": start_date.strftime("%B %Y"),
        "prev_month_str": prev_month.strftime("%Y-%m"),
        "next_month_str": next_month.strftime("%Y-%m"),
    })
