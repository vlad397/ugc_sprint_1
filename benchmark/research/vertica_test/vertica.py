import cProfile
import io
import json
import pstats
from statistics import mean, median
from uuid import UUID

import vertica_python
from mimesis import Generic
from vertica_python.vertica.cursor import Cursor

fake = Generic()


CHUNK = 500  # кол-во элементов в пачке
VALUE_FOR_1 = 2000  # кол-во данных для отправки по одному
VALUE_FOR_500 = 1000000  # кол-во данных для отправки пачками
# названия для файлов
NAME_FOR_1_FILE = "one_result"
NAME_FOR_500_FILE = "five_hundred_result"
NAME_FOR_GET_DATA = "get_data_result"
NAME_FOR_SELECT_DATA = "select_result"


def test_select_by_ids(cursor: Cursor, user: UUID, film: UUID) -> bool:
    """Функция тестирования времени выполнения запроса"""
    with cProfile.Profile() as pr:
        cursor.execute(f"""SELECT * FROM views WHERE user_id='{user}' and film_id='{film}';""")
    stats = io.StringIO()
    ps = pstats.Stats(pr, stream=stats)
    ps.print_stats()
    value = stats.getvalue()

    generate_file(value, NAME_FOR_SELECT_DATA)

    return True


def get_data(cursor: Cursor) -> tuple:
    """Функция для получения записи для тестирования select-запроса"""
    with cProfile.Profile() as pr:
        cursor.execute("""SELECT * FROM views;""")
    stats = io.StringIO()
    ps = pstats.Stats(pr, stream=stats)
    ps.print_stats()
    value = stats.getvalue()

    generate_file(value, NAME_FOR_GET_DATA)

    result = cursor.fetchone()
    return result[1], result[2]


def generate_results(name: str) -> dict:
    """Функция для подсчета среднего значения, медианы и суммы значений
    на основе записанных в файл данных"""
    result_list = []

    with open(f"vertica_test/{name}.txt", "r") as file:
        for line in file:
            # Возьмем из файла только значения времени
            split_line = line.strip().split(" ")
            result_list.append(float(split_line[-2]))

    result = {"Среднее, с.": mean(result_list), "Медиана, с.": median(result_list), "Сумма, с.": sum(result_list)}

    with open(f"vertica_test/{name}.txt", "a", encoding="utf8") as file:
        json.dump(result, file, ensure_ascii=False)

    return result


def generate_data(value: int) -> list:
    """Функция для генерации списка данных"""
    generated_list: list[list] = [
        [
            fake.cryptographic.uuid_object(),
            fake.cryptographic.uuid_object(),
            fake.datetime.timestamp(),
            fake.datetime.datetime(start=2010, end=2022),
            fake.datetime.date(start=2010, end=2022),
        ]
        for _ in range(value)
    ]
    return generated_list


def generate_file(value: str, name: str) -> bool:
    """Функция для записи данных тестирования в файл"""
    # Уберем из результатов тестирования ненужные данные
    split_result = value.split("\n\n")
    result = split_result[0].replace("   ", "")

    with open(f"vertica_test/{name}.txt", "a") as file:
        file.write(result + "\n")

    return True


def test_vertica_1_at_time(cursor: Cursor) -> bool:
    """Функция для тестирования времени записи 2000 объектов при отправке
    по одному элементу"""
    generated_list = generate_data(VALUE_FOR_1)

    for row in generated_list:
        with cProfile.Profile() as pr:
            cursor.execute(
                """INSERT INTO views 
                (user_id, film_id, film_timestamp, event_time, event_date_part) 
                VALUES(?, ?, ?, ?, ?)""",
                row,
                use_prepared_statements=True,
            )
        stats = io.StringIO()
        ps = pstats.Stats(pr, stream=stats)
        ps.print_stats()
        value = stats.getvalue()

        generate_file(value, NAME_FOR_1_FILE)

    return True


def test_vertica_500_at_time(cursor: Cursor) -> bool:
    """Функция для тестирования времени записи 2000 объектов при отправке
    по 500 элементов пачками"""
    generated_list = generate_data(VALUE_FOR_500)

    for rows in range(0, len(generated_list), CHUNK):
        with cProfile.Profile() as pr:
            cursor.executemany(
                """INSERT INTO views """
                """(user_id, film_id, film_timestamp, event_time, event_date_part) """
                """VALUES(?, ?, ?, ?, ?)""",
                list(generated_list[rows: rows + CHUNK]),  # срезами перемещаемся по списку
                use_prepared_statements=True,
            )
        stats = io.StringIO()
        ps = pstats.Stats(pr, stream=stats)
        ps.print_stats()
        value = stats.getvalue()

        generate_file(value, NAME_FOR_500_FILE)

    return True


if __name__ == "__main__":

    connection_info = {
        "host": "127.0.0.1",
        "port": 5433,
        "user": "dbadmin",
        "password": "",
        "database": "docker",
        "autocommit": True,
    }

    with vertica_python.connect(**connection_info) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS views (
            id IDENTITY,
            user_id uuid NOT NULL,
            film_id uuid NOT NULL,
            film_timestamp integer NOT NULL,
            event_time timestamp NOT NULL,
            event_date_part date NOT NULL);"""
        )

        test_vertica_500_at_time(cursor)
        print(generate_results(NAME_FOR_500_FILE))

        test_vertica_1_at_time(cursor)
        print(generate_results(NAME_FOR_1_FILE))

        user, film = get_data(cursor)
        print(generate_results(NAME_FOR_GET_DATA))

        test_select_by_ids(cursor, user, film)
        print(generate_results(NAME_FOR_SELECT_DATA))
