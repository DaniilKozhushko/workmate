import json
from datetime import datetime
from collections import defaultdict


def read_log_files(file_paths: list[str] | None) -> list[dict]:
    """
    Извлекает строки логов из переданных json-файлов и возвращает список словарей.

    :param file_paths: путь(и) к файлу(ам)
    :return: список словарей (строк логов), если файл непустой
    """

    entries = []

    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    try:
                        # десериализация строк json-файла
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON-line in file {file_path} in line {line}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")

    return entries


def average_response_report(
    log_entries: list[dict], date: str | None = None, period: list[str] | None = None
) -> list[list]:
    """
    Формирует список со строками отчёта - среднее время ответа. Учитывает дату/период, если они были переданы.

    :param log_entries: список словарей (строк логов)
    :param date: дата за которую нужно сформировать отчёт
    :param period: период за который нужно сформировать отчёт
    :return: список строк для вывода отчёта
    """
    # по умолчанию значение является пустым словарём
    stats = defaultdict(list)

    for entry in log_entries:
        # получение необходимых значений записи
        # можно оперативно подставлять желаемые ключи для добавления новых отчётов
        handler = entry.get("url")
        response_time = entry.get("response_time")

        # простая проверка на присутствие необходимых данных
        if not handler or response_time is None:
            continue

        try:
            # проверка корректности метки
            timestamp = datetime.fromisoformat(entry.get("@timestamp")).date()
        except ValueError as ve:
            print(ve)
            continue

        # фильтрация по заданной дате
        if date and timestamp != date:
            continue

        # фильтрация по заданному периоду
        if period:
            start_date, end_date = period
            if not (start_date <= timestamp <= end_date):
                continue

        stats[handler].append(response_time)

    # ошибка, что в указанную дату (период) нет записей
    if not stats:
        if date:
            raise ValueError(f"No log entries found for date {date}.")
        elif period:
            raise ValueError(
                f"No log entries found for period {start_date} -> {end_date}."
            )

    # формирование списка для вывода отчёта
    report = []
    for handler, times in stats.items():
        # количество обращений к эндпоинту
        total = len(times)

        # среднее время ответа
        avg_resp_time = sum(times) / total

        report.append([handler, total, round(avg_resp_time, 3)])

    return report
