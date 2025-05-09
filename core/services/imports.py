import csv
import json
import logging
from datetime import datetime
from django.db import transaction
from core.models import (
    Building, Department, PrinterModel, Printer, User,
    PrintEvent, Computer, Port
)
from django.db.models import Q

logger = logging.getLogger(__name__)

def import_users_from_csv(file):
    created, errors = 0, []

    decoded = file.read().decode("utf-8-sig").splitlines()
    reader = csv.DictReader(decoded)

    for row in reader:
        try:
            username = row.get("SamAccountName", "").strip()
            fio = row.get("DisplayName", "").strip()
            dept_code = row.get("OU", "").strip().lower()

            if not username or not dept_code:
                continue

            department, _ = Department.objects.get_or_create(
                code=dept_code,
                defaults={"name": dept_code.upper()}
            )

            user, created_user = User.objects.get_or_create(
                username=username.lower(),
                defaults={
                    "fio": fio or username,
                    "department": department
                }
            )

            if created_user:
                created += 1

        except Exception as e:
            msg = f"🔥 Ошибка в строке {row}: {str(e)}"
            logger.exception(msg)
            errors.append(msg)

    logger.info("👤 Импорт пользователей завершён: создано %d, ошибок: %d", created, len(errors))
    return {"created": created, "errors": errors}

def import_print_events_from_json(events):
    created, errors = 0, []

    for e in events:
        try:
            with transaction.atomic():
                username = (e.get("Param3") or "").strip().lower()
                document_name = e.get("Param2") or ""
                document_id = int(e.get("Param1") or 0)
                byte_size = int(e.get("Param7") or 0)
                pages = int(e.get("Param8") or 0)
                timestamp_ms = int(str(e.get("TimeCreated", "0")).replace("/Date(", "").replace(")/", ""))
                timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
                job_id = e.get("JobID") or "UNKNOWN"

                if PrintEvent.objects.filter(job_id=job_id).exists():
                    continue

                # Разбор принтера
                printer_name = (e.get("Param5") or "")
                parts = printer_name.lower().split("-")
                if len(parts) != 5:
                    errors.append(f"❌ Неверный формат принтера: {printer_name}")
                    continue

                model_code, bld_code, dept_code, room, index = parts
                printer_index = int(index)

                building, _ = Building.objects.get_or_create(code=bld_code, defaults={"name": bld_code.upper()})
                department, _ = Department.objects.get_or_create(code=dept_code, defaults={"name": dept_code.upper()})
                model, _ = PrinterModel.objects.get_or_create(
                    code=model_code,
                    defaults={
                        "manufacturer": model_code.split()[0],
                        "model": model_code
                    }
                )

                printer, _ = Printer.objects.get_or_create(
                    room_number=room,
                    printer_index=printer_index,
                    building=building,
                    defaults={
                        "model": model,
                        "department": department,
                        "is_active": True
                    }
                )

                user = User.objects.filter(username=username).first()
                if not user:
                    errors.append(f"❌ Пользователь не найден: {username}")
                    continue

                # Разбор компьютера
                computer_name = (e.get("Param4") or "").strip().lower()
                computer = None
                if computer_name:
                    computer = Computer.objects.filter(hostname=computer_name).first()
                    if not computer and len(computer_name.split("-")) == 4:
                        bld, dept, room_num, num = computer_name.split("-")
                        building_c, _ = Building.objects.get_or_create(code=bld, defaults={"name": bld.upper()})
                        department_c, _ = Department.objects.get_or_create(code=dept, defaults={"name": dept.upper()})
                        computer = Computer.objects.create(
                            hostname=computer_name,
                            building=building_c,
                            department=department_c,
                            room_number=room_num,
                            number_in_room=int(num) if num.isdigit() else 0
                        )
                    elif not computer:
                        computer = Computer.objects.create(
                            hostname=computer_name,
                            full_name=computer_name
                        )

                # Разбор порта
                port_name = (e.get("Param6") or "").strip().lower()
                port = None
                port_parts = port_name.split("-")
                if len(port_parts) == 5:
                    port_model, port_bld, port_dept, port_room, port_index = port_parts
                    port_index = int(port_index) if port_index.isdigit() else 0
                    pb, _ = Building.objects.get_or_create(code=port_bld, defaults={"name": port_bld.upper()})
                    pd, _ = Department.objects.get_or_create(code=port_dept, defaults={"name": port_dept.upper()})
                    port, _ = Port.objects.get_or_create(
                        name=port_name,
                        defaults={
                            "building": pb,
                            "department": pd,
                            "room_number": port_room,
                            "printer_index": port_index
                        }
                    )

                PrintEvent.objects.create(
                    document_id=document_id,
                    document_name=document_name,
                    user=user,
                    printer=printer,
                    job_id=job_id,
                    timestamp=timestamp,
                    byte_size=byte_size,
                    pages=pages,
                    computer=computer,
                    port=port
                )
                created += 1

        except Exception as ex:
            msg = f"🔥 Ошибка события: {str(ex)}"
            logger.exception(msg)
            errors.append(msg)

    logger.info("🖨️ Импорт событий завершён: создано %d, ошибок: %d", created, len(errors))
    return {"created": created, "errors": errors}
