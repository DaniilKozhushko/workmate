from main import main


def test_main_runs(monkeypatch, tmp_path):
    # создаю временный файл с логом
    log_file = tmp_path / "log.json"
    log_file.write_text(
        '{"@timestamp": "2025-06-22T12:00:00+00:00", "url": "/api/test", "response_time": 0.1}\n'
    )

    monkeypatch.setattr("sys.argv", ["main.py", "--file", str(log_file)])

    # main не должен падать
    main()
