from datetime import datetime
from django.shortcuts import render
from django.db.models import Sum, Q
from django.http import HttpResponse
import io
import xlsxwriter
from core.models import PrintEvent, Department, Printer, PrinterModel, User

def index(request):
    return render(request, "core/index.html")

def users_list_view(request):
    q = request.GET.get("q", "").strip()
    users = User.objects.all()
    if q:
        users = users.filter(Q(username__icontains=q) | Q(fio__icontains=q))
    users = users.order_by('username')
    return render(request, "core/users.html", {"users": users})

def print_events_view(request):
    dept_code = request.GET.get("dept", "").strip().lower()
    start_date_str = request.GET.get("start_date", "").strip()
    end_date_str = request.GET.get("end_date", "").strip()

    base_query = PrintEvent.objects.select_related('user', 'printer__model', 'printer__building', 'printer__department')

    if dept_code:
        base_query = base_query.filter(printer__department__code__icontains=dept_code)

    if start_date_str:
        try:
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
            base_query = base_query.filter(timestamp__gte=start_dt)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            base_query = base_query.filter(timestamp__lte=end_dt)
        except ValueError:
            pass

    total_pages = base_query.aggregate(Sum('pages'))['pages__sum'] or 0
    events = base_query.order_by('-timestamp')[:500]
    departments = Department.objects.order_by('code')

    return render(request, "core/print_events.html", {
        "events": events,
        "total_pages": total_pages,
        "departments": departments,
        "selected_dept": dept_code,
        "start_date": start_date_str,
        "end_date": end_date_str
    })

def print_tree_view(request):
    start_date_str = request.GET.get("start_date", "").strip()
    end_date_str = request.GET.get("end_date", "").strip()

    query = PrintEvent.objects.select_related('printer__department', 'printer__model', 'user')

    if start_date_str:
        try:
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
            query = query.filter(timestamp__gte=start_dt)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(timestamp__lte=end_dt)
        except ValueError:
            pass

    temp_tree = {}
    total_pages = 0

    for event in query:
        dept_name = f"{event.printer.department.code} — {event.printer.department.name}"
        printer_name = f"{event.printer.model.code}-{event.printer.room_number}-{event.printer.printer_index}"
        user_name = event.user.fio
        doc_name = event.document_name

        total_pages += event.pages

        temp_tree.setdefault(dept_name, {"total": 0, "printers": {}})
        dept = temp_tree[dept_name]
        dept["total"] += event.pages

        dept["printers"].setdefault(printer_name, {"total": 0, "users": {}})
        printer = dept["printers"][printer_name]
        printer["total"] += event.pages

        printer["users"].setdefault(user_name, {"total": 0, "docs": {}})
        user = printer["users"][user_name]
        user["total"] += event.pages

        user["docs"].setdefault(doc_name, []).append({
            "pages": event.pages,
            "timestamp": event.timestamp
        })

    tree = temp_tree

    return render(request, "core/print_tree.html", {
        "tree": tree,
        "total_pages": total_pages,
        "start_date": start_date_str,
        "end_date": end_date_str
    })

def export_tree_excel_view(request):
    start_date_str = request.GET.get("start_date", "").strip()
    end_date_str = request.GET.get("end_date", "").strip()

    query = PrintEvent.objects.select_related('printer__department', 'printer__model', 'user')

    if start_date_str:
        try:
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
            query = query.filter(timestamp__gte=start_dt)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(timestamp__lte=end_dt)
        except ValueError:
            pass

    rows = query.order_by(
        'printer__department__name',
        'printer__room_number',
        'user__fio',
        'timestamp'
    )

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    ws = workbook.add_worksheet("Print Events")

    headers = ["Отдел", "Принтер", "ФИО", "Документ", "Страниц", "Дата"]
    for col, h in enumerate(headers):
        ws.write(0, col, h)

    for i, event in enumerate(rows, start=1):
        printer_name = f"{event.printer.model.code}-{event.printer.room_number}-{event.printer.printer_index}"
        ws.write(i, 0, f"{event.printer.department.code} — {event.printer.department.name}")
        ws.write(i, 1, printer_name)
        ws.write(i, 2, event.user.fio)
        ws.write(i, 3, event.document_name)
        ws.write(i, 4, event.pages)
        ws.write(i, 5, event.timestamp.strftime('%d.%m.%Y %H:%M'))

    workbook.close()
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="print_events_tree.xlsx"'
    return response
