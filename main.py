import argparse
import utils.utils as u
from datetime import datetime
from tabulate import tabulate


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """
    Парсит переданные скрипту аргументы для программы формирования отчёта лог-файлов..

    :return: Namespace с атрибутами
    """

    def valid_date(date_str: str):
        """
        Проверка валидности введённой пользователем даты.

        :param date_str: дата, введённая пользователем
        :return: datetime или ошибка типа ValueError
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"{date_str} - is not a valid date. Format must be YYYY-MM-DD."
            )

    # создание объекта парсера с описанием программы
    parser = argparse.ArgumentParser(
        description="Formation and printing of reports on log files"
    )

    # добавление аргументов
    parser.add_argument(
        "-f", "--file", nargs="+", required=True, help="Path(s) to log(s)."
    )
    parser.add_argument("-r", "--report", default="average", help="Type of the report.")
    parser.add_argument(
        "-d",
        "--date",
        default=None,
        type=valid_date,
        help="Date for which the report should be printed. Format: YYYY-MM-DD",
    )
    parser.add_argument(
        "-p",
        "--period",
        nargs=2,
        default=None,
        type=valid_date,
        metavar=("START_DATE", "END_DATE"),
        help="Period for which the report should be printed. Format: YYYY-MM-DD YYYY-MM-DD",
    )

    parsed_args = parser.parse_args(args)

    # проверка, что период корректен: start_date <= end_date
    if parsed_args.period:
        start_date, end_date = parsed_args.period
        if start_date > end_date:
            parser.error(
                f"Start date {start_date} can not be after the end date {end_date}."
            )

    return parsed_args


def print_report(report) -> None:
    """
    Печатает отчёт в формате "simple".

    :param report: список строк для вывода отчёта
    :return: None
    """
    print(
        tabulate(
            report,
            headers=["", "handler", "total", "avg_response_time"],
            tablefmt="simple",
        )
    )


def main():
    try:
        # получение аргументов, переданных при запуске скрипта
        args = parse_args()

        # чтение строк логов из файла(ов)
        logs = u.read_log_files(args.file)

        if not logs:
            raise ValueError(
                "There are no logs in the transferred files or the paths are incorrect."
            )

        if args.report == "average":
            try:
                # формирование отчёта для печати
                report = u.average_response_report(
                    log_entries=logs, date=args.date, period=args.period
                )
            except ValueError as ve:
                print(ve)
                return

            # сортировка по количеству запросов по убыванию
            report.sort(key=lambda x: x[1], reverse=True)

            # добавление порядковых номеров
            for idx, row in enumerate(report):
                row.insert(0, idx)

            print_report(report)
        else:
            print(f"Report type {args.report} not implemented.")
    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
