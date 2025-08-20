import pytest
import utils.utils as u
from datetime import date

# фиксирую значение логов для тестов
@pytest.fixture
def logs():
    return [
        {
            "@timestamp": "2025-06-22T12:00:00+00:00",
            "url": "/api/test1",
            "response_time": 0.1,
        },
        {
            "@timestamp": "2025-06-23T12:00:00+00:00",
            "url": "/api/test2",
            "response_time": 0.2,
        },
        {
            "@timestamp": "2025-06-23T12:30:00+00:00",
            "url": "/api/test2",
            "response_time": 0.4,
        },
    ]


def test_average_report_empty_list():
    # проверка, что пустой список возвращает пустой отчёт
    report = u.average_response_report([])
    assert report == []


def test_average_report_invalid_timestamp(monkeypatch):
    # лог с некорректным timestamp
    logs = [{"@timestamp": "invalid-date", "url": "/api/test", "response_time": 0.1}]
    # функция должна пропускать некорректные строки и не падать
    report = u.average_response_report(logs)
    assert report == []


def test_average_report_period_boundaries(logs):
    # проверка фильтрации по периоду (включительно)
    start = date(2025, 6, 22)
    end = date(2025, 6, 23)
    report = u.average_response_report(logs, period=[start, end])
    # обе группы должны попасть в отчёт
    handlers = [r[0] for r in report]
    assert "/api/test1" in handlers
    assert "/api/test2" in handlers


def test_average_report_period_exclusive(logs):
    # период, в который не попадает ни одна запись — должно быть исключение
    start = date(2025, 6, 24)
    end = date(2025, 6, 25)
    with pytest.raises(ValueError) as excinfo:
        u.average_response_report(logs, period=[start, end])
    assert "No log entries found for period" in str(excinfo.value)


def test_average_report_date_filter(logs):
    # фильтрация по дате
    report = u.average_response_report(logs, date=date(2025, 6, 22))
    assert len(report) == 1
    assert report[0][0] == "/api/test1"
