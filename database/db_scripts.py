from const import *
import psycopg2
import os
import shutil
import datetime as dt
from datetime import date
import re
import pandas as pd
import string
import itertools
from collections import defaultdict



# Добавление пользователя
def add_user(user_name, where_find, telegram_id):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute(f"INSERT INTO users (user_name,where_find,telegram_id) VALUES (%s,%s,%s"
                        f")", (user_name, where_find, telegram_id))
    conn.commit()
    curs.close()
    conn.close()


def get_user_nick(telegram_id):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute("SELECT user_name FROM users WHERE telegram_id = %s", (telegram_id,))
    user = '@' + curs.fetchone()[0]
    curs.close()
    conn.close()
    return user


########################################################################################################################
# # Добавляем статистику
def add_user_statistic(user_id, content_type, choose_content):
    if choose_content not in KEYBOARD_CALL:
        try:
            conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
            curs = conn.cursor()
            curs.execute(f"INSERT INTO users_statistic (user_id, content_type, content_name) VALUES (%s,%s,%s)", (user_id, content_type, choose_content))
            conn.commit()
            curs.close()
            conn.close()
        except Exception as e:
            print(f'Ошибка записи статистики: {e}')


########################################################################################################################
# Проверка наличия пользователя
def select_user_id(telegram_id):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    user = curs.fetchone()
    curs.close()
    conn.close()
    return user is not None

# получаем всех пользователей из базы
def select_all_users():
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute("SELECT * FROM users")
    result1 = curs.fetchall()
    result = [t[3] for t in result1]
    curs.close()
    conn.close()
    return result

# получаем список всех пользователей и ников
def select_user_list():
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute("SELECT * FROM users")
    result1 = curs.fetchall()
    result = [[t[1],t[3]] for t in result1]
    curs.close()
    conn.close()
    return result


# извлекаем все типы аккордов
def select_all_chord_types():
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute("SELECT * FROM chord_type")
    result = curs.fetchall()
    curs.close()
    conn.close()
    return result


# # извлекаем ссылку на аккорд
def select_chord(chord):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute(f"SELECT link, description, chord FROM chords WHERE chord = %s", (chord,))
    result = curs.fetchone()
    curs.close()
    conn.close()
    return result


# получаем тип данного аккорда
def type_chord(chord):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute(f"SELECT type_id FROM chords WHERE chord = %s", (chord,))
    result = curs.fetchone()[0]
    curs.close()
    conn.close()
    return result



def select_band(letter):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute(f"SELECT band FROM bands WHERE letter = %s", (letter,))
    result1 = curs.fetchall()
    result = [t[0] for t in result1]
    curs.close()
    conn.close()
    return sorted(result, key=str.lower)
###############################################################################################################

# получаем список всех групп
def select_all_band():
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute(f"SELECT DISTINCT band FROM bands")
    result1 = curs.fetchall()
    result = [t[0] for t in result1]
    curs.close()
    conn.close()
    return result


# количество страниц муз групп на определенную букву
def count_page_band(letter):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute(f"SELECT MAX(page_band) FROM bands WHERE letter = %s", (letter,))
    result = curs.fetchall()[0][0]
    curs.close()
    conn.close()
    return result


# количество страниц песен группы
def count_page_song_band(band):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute(f"SELECT MAX(page_song) FROM songs WHERE band = %s", (band,))
    result = curs.fetchall()[0][0]
    curs.close()
    conn.close()
    return result



def select_song(band):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute(f"SELECT song_name FROM songs WHERE band = %s", (band,))
    result1 = curs.fetchall()
    result = [t[0] for t in result1]
    curs.close()
    conn.close()
    return sorted(result, key=str.lower)


# получаем список идентичных песен
def generate_variants(name_part):
    # Находим позиции всех букв 'е' и 'ё' в части названия после ' - '
    positions = [i for i, ch in enumerate(name_part.lower()) if ch in ('е', 'ё')]

    # Определяем границы слов
    # Предположим, что слова разделены пробелами
    word_boundaries = [0]
    for i, ch in enumerate(name_part):
        if ch == ' ':
            word_boundaries.append(i + 1)
    word_boundaries.append(len(name_part))

    def is_in_end_or_penultimate(pos):
        # Проверяем, входит ли позиция в конец или предпоследний символ слова
        for start in word_boundaries:
            end = next((b for b in word_boundaries if b > start), len(name_part))
            length = end - start
            # Позиция внутри этого слова
            if start <= pos < end:
                # Если позиция в конце или предпоследней позиции этого слова
                if pos >= end - 2:
                    return True
        return False

    # Создаем список вариантов для каждой позиции: оставить как есть или заменить на другую букву
    options = []
    for i in range(len(name_part)):
        if i in positions:
            # Проверяем, не в конце/предпоследней позиции слова
            if is_in_end_or_penultimate(i):
                # Если да — оставляем только оригинальный символ
                options.append([name_part[i]])
            else:
                # Иначе — оба варианта: 'е' и 'ё'
                options.append(['е', 'ё'])
        else:
            options.append([name_part[i]])

    # Генерируем все комбинации
    variants = set()
    for combo in itertools.product(*options):
        variant = ''.join(combo)
        variants.add(variant)
    print(len(variants))
    return variants


def remove_suff(text):
    return re.sub(r'_\d.*', '', text)


def select_songs_group_song(full_name):
    full_name = remove_suff(full_name)

    # Разделяем название на группу и название песни по разделителю ' - '
    parts = full_name.split(' - ', 1)

    if len(parts) == 2:
        group_name, song_name_part = parts[0], parts[1]
    else:
        # Если разделитель не найден, считаем всю строку названием песни
        group_name, song_name_part = '', full_name

    # Генерируем вариации только для части после ' - '
    variants = generate_variants(song_name_part)

    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()

        results_set = set()

        for variant in variants:
            # Объединяем неизменную часть с вариацией
            search_name = f"{group_name} - {variant}" if group_name else variant
            pattern = f"{search_name}%"
            query = "SELECT * FROM songs WHERE song_name ILIKE %s;"
            curs.execute(query, (pattern,))
            results = curs.fetchall()
            results_set.update(results)

        curs.close()
        conn.close()

        return list(results_set)

    except Exception as e:
        print("Ошибка при поиске песен:", e)
        return []


########################################################################################################################

# получить аккорды для песни
def select_chord_song_info(song: str):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute(f"SELECT * FROM songs WHERE song_name = %s", (song,))
        result = curs.fetchone()
        curs.close()
        conn.close()
        return result
    except Exception as e:
        print(e)
        return []


# Для длинных названий
def escape_regex_string(s: str) -> str:
    return re.sub(r'([(){}[\]\\.^$|?*+])', r'\\\1', s)


def select_long_chord_song_info(song: str):
    prefix = song[:30]
    suffix = song[-1]

    # Экранируем специальные символы
    escaped_prefix = escape_regex_string(prefix)
    escaped_suffix = escape_regex_string(suffix)

    # Конструируем регулярное выражение
    pattern = f"^{escaped_prefix}.*{escaped_suffix}$"

    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    query = "SELECT * FROM songs WHERE song_name ~ %s"
    curs.execute(query, (pattern,))

    result = curs.fetchone()
    curs.close()
    conn.close()
    return result

# информация в профиле пользователя
def select_user_info(telegram_id):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute(f"SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    result = list(curs.fetchall()[0])
    curs.close()
    conn.close()
    return result


# получение списка статей
def select_all_articles(page: int = 1):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute("SELECT name_article FROM articles WHERE page = %s", (page,))
    result = [i[0] for i in curs.fetchall()]
    curs.close()
    conn.close()
    return result


# получение ссылки на статью
def select_article(name_article):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute(f"SELECT * FROM articles WHERE name_article = %s", (name_article,))
    result = curs.fetchall()[0]
    curs.close()
    conn.close()
    return result

# Статистика
########################################################################################################################
# статистика подсчёт количества пользователей
def statistics_users():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("SELECT COUNT(*) FROM users")
        result = curs.fetchall()
        curs.close()
        conn.close()
        if not result[0][0]:
            return 0
        else:
            return result[0][0]
    except:
        return 0


# Статистика зарегистрированных пользователей сегодня
def statistics_users_today():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        today_date = dt.datetime.now().date()
        curs.execute(
            "SELECT COUNT(*) FROM users WHERE DATE(reg_time) = %s",
            (today_date,)
        )
        result = curs.fetchall()
        curs.close()
        conn.close()
        if not result[0][0]:
            return 0
        else:
            return result[0][0]
    except:
        return 0

# Статистика зарегистрированных пользователей за текущий месяц
def statistics_users_current_month():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        now = dt.datetime.now()
        current_year = now.year
        current_month = now.month

        # Первый день текущего месяца
        start_of_month = dt.date(current_year, current_month, 1)
        # Первый день следующего месяца
        if current_month == 12:
            next_month = dt.date(current_year + 1, 1, 1)
        else:
            next_month = dt.date(current_year, current_month + 1, 1)

        curs.execute(
            "SELECT COUNT(*) FROM users WHERE reg_time >= %s AND reg_time < %s",
            (start_of_month, next_month)
        )
        result = curs.fetchall()
        curs.close()
        conn.close()
        if not result[0][0]:
            return 0
        else:
            return result[0][0]
    except:
        return 0


# за текущий год зарегистрировалось
def statistics_users_current_year():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        now = dt.datetime.now()
        current_year = now.year

        # Первый день текущего года
        start_of_year = dt.date(current_year, 1, 1)
        # Текущая дата
        today = dt.date(current_year, now.month, now.day)

        curs.execute(
            "SELECT COUNT(*) FROM users WHERE reg_time >= %s AND reg_time <= %s",
            (start_of_year, today)
        )
        result = curs.fetchall()
        curs.close()
        conn.close()

        return result[0][0] if result and result[0][0] else 0
    except:
        return 0


# статистика количества песен
def statistics_song():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("SELECT COUNT(*) FROM songs")
        result = curs.fetchall()
        curs.close()
        conn.close()
        if not result[0][0]:
            return 0
        else:
            return result[0][0]
    except:
        return 0

# статистика песен в избранном
def statistics_fav_song():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("SELECT COUNT(*) FROM favorite_songs WHERE telegram_id != %s",(GENERAL_ADMIN,))
        result = curs.fetchall()
        curs.close()
        conn.close()
        if not result[0][0]:
            return 0
        else:
            return result[0][0]
    except:
        return 0

# добавили в избранное сегодня
def statistics_fav_song_today():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        today_date = dt.datetime.now().date()
        curs.execute(
            "SELECT COUNT(*) FROM favorite_songs WHERE DATE(time_update) = %s",
            (today_date,)
        )
        result = curs.fetchall()
        curs.close()
        conn.close()
        if not result[0][0]:
            return 0
        else:
            return result[0][0]
    except:
        return 0

# добавили в избранное за месяц
def statistics_fav_song_month():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        now = dt.datetime.now()
        current_year = now.year
        current_month = now.month

        start_of_month = dt.date(current_year, current_month, 1)
        if current_month == 12:
            next_month = dt.date(current_year + 1, 1, 1)
        else:
            next_month = dt.date(current_year, current_month + 1, 1)

        curs.execute(
            "SELECT COUNT(*) FROM favorite_songs WHERE time_update >= %s AND time_update < %s",
            (start_of_month, next_month)
        )
        result = curs.fetchall()
        curs.close()
        conn.close()
        if not result[0][0]:
            return 0
        else:
            return result[0][0]
    except:
        return 0


# Статистика просмотра контента
########################################################################################################################
# статистика посещений сегодня
def statistics_use_today(content_type:int = 0):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()

        today_start = dt.datetime.combine(dt.date.today(), dt.time.min)
        today_end = dt.datetime.combine(dt.date.today(), dt.time.max)

        if content_type == 0:
            # Получить сумму уникальных посещений по часам
            curs.execute(
                """
                SELECT SUM(hourly_unique) FROM (
                    SELECT COUNT(DISTINCT user_id) AS hourly_unique
                    FROM views_type
                    WHERE time_update BETWEEN %s AND %s
                    GROUP BY EXTRACT(HOUR FROM time_update)
                ) sub;
                """,
                (today_start, today_end)
            )
            result = curs.fetchone()[0]
            total_visits = result if result is not None else 0
        else:
            # Общее число просмотров по типу контента за сегодня
            curs.execute(
                """
                SELECT COUNT(*)
                FROM views_type
                WHERE time_update >= %s AND time_update <= %s AND content_type = %s
                """,
                (today_start, today_end, content_type)
            )
            total_visits = curs.fetchone()[0]

        curs.close()
        conn.close()

        return total_visits

    except Exception as e:
        print("Ошибка при подсчёте:", e)
        return 0

# новая статистика на сегодня
def statistic_use_today_2():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        today_date = date.today()

        # Запрос для получения данных за сегодня
        query = """
                   SELECT COUNT(DISTINCT user_id)
                   FROM users_statistic
                   WHERE DATE(time) = %s AND user_id != %s; 
               """

        curs.execute(query, (today_date, GENERAL_ADMIN))
        results = curs.fetchall()[0][0]
        return results
    except Exception as e:
        # Можно логировать ошибку e для отладки
        return 0


# статистика за текущий месяц
def statistics_use_month(content_type:int = 0):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        now = dt.datetime.now()
        current_year = now.year
        current_month = now.month

        # Начало и конец месяца
        start_of_month = dt.date(current_year, current_month, 1)
        if current_month == 12:
            next_month = dt.date(current_year + 1, 1, 1)
        else:
            next_month = dt.date(current_year, current_month + 1, 1)
        if content_type == 0:
            # Подсчет ежедневных уникальных пользователей
            delta_days = (next_month - start_of_month).days
            total_unique_users = 0

            for day_offset in range(delta_days):
                day_start = start_of_month + dt.timedelta(days=day_offset)
                day_end = day_start + dt.timedelta(days=1)

                curs.execute(
                    """
                    SELECT COUNT(DISTINCT user_id) 
                    FROM views_type 
                    WHERE DATE(time_update) >= %s AND DATE(time_update) < %s
                    """,
                    (day_start, day_end)
                )
                result = curs.fetchone()
                daily_count = result[0] if result and result[0] is not None else 0
                total_unique_users += daily_count

        # Подсчет общего количества просмотров по типу контента за месяц
        else:
            # Для конкретного типа контента
            curs.execute(
                """
                SELECT COUNT(user_id) 
                FROM views_type 
                WHERE DATE(time_update) >= %s AND DATE(time_update) < %s AND content_type = %s
                """,
                (start_of_month, next_month, content_type)
            )
            total_unique_users = curs.fetchone()[0]

        curs.close()
        conn.close()
        return total_unique_users


    except Exception as e:
        # Можно логировать ошибку e для отладки
        return 0


# посещения за год

def statistics_use_year(content_type:int = 0):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        now = dt.datetime.now()
        current_year = now.year

        # Первый день текущего года
        start_of_year = dt.date(current_year, 1, 1)
        # Текущая дата
        today = dt.date(current_year, now.month, now.day)

        if content_type == 0:
            # Считаем сумму уникальных посещений по месяцам:
            # для каждого месяца считаем уникальных пользователей и суммируем
            curs.execute(
                """
                SELECT COALESCE(SUM(monthly_unique), 0) FROM (
                    SELECT COUNT(DISTINCT user_id) AS monthly_unique
                    FROM views_type
                    WHERE DATE(time_update) >= %s AND DATE(time_update) <= %s
                    GROUP BY EXTRACT(MONTH FROM time_update)
                ) sub;
                """,
                (start_of_year, today)
            )
        else:
            # Все просмотры по типу за год
            curs.execute(
                "SELECT COUNT(user_id) FROM views_type WHERE DATE(time_update) >= %s AND DATE(time_update) <= %s AND content_type = %s",
                (start_of_year, today, content_type)
            )

        result = curs.fetchone()
        curs.close()
        conn.close()

        return result[0] if result and result[0] else 0

    except:
        return 0

# статистика посещений по разделам и всё вместе
def add_user_views(user_id,type_views):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("INSERT INTO views_type (user_id,content_type) VALUES (%s, %s);", (user_id,type_views))
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        print("Ошибка при при добавлении песни:", e)

# статистика постоянных пользователей
# TODO не работает
def get_non_registered_regular_users_counts():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()

        now = dt.datetime.now()

        # Периоды
        day_start = dt.datetime(now.year, now.month, now.day)
        day_end = day_start + dt.timedelta(days=1)

        month_start = dt.datetime(now.year, now.month, 1)
        if now.month == 12:
            next_month_start = dt.datetime(now.year + 1, 1, 1)
        else:
            next_month_start = dt.datetime(now.year, now.month + 1, 1)

        year_start = dt.datetime(now.year, 1, 1)
        year_end = dt.datetime(now.year + 1, 1, 1)

        # За день
        curs.execute("""
            SELECT COUNT(DISTINCT v.user_id) FROM views_type v
            WHERE v.user_id NOT IN (SELECT user_id FROM users)
              AND v.time_update >= %s AND v.time_update < %s;
        """, (day_start, day_end))
        count_day = curs.fetchone()[0]

        # За месяц
        curs.execute("""
            SELECT COUNT(DISTINCT v.user_id) FROM views_type v
            WHERE v.user_id NOT IN (SELECT user_id FROM users)
              AND v.time_update >= %s AND v.time_update < %s;
        """, (month_start, next_month_start))
        count_month = curs.fetchone()[0]

        # За год
        curs.execute("""
            SELECT COUNT(DISTINCT v.user_id) FROM views_type v
            WHERE v.user_id NOT IN (SELECT user_id FROM users)
              AND v.time_update >= %s AND v.time_update < %s;
        """, (year_start, year_end))
        count_year = curs.fetchone()[0]

        curs.close()
        conn.close()

        return {
            'day': count_day,
            'month': count_month,
            'year': count_year
        }

    except Exception as e:
        print("Ошибка:", e)
        return {'day': 0, 'month': 0, 'year': 0}

# топ 10 пользователей по просмотрам
def top_10_users_by_views():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        query = """
            SELECT u.user_name, COUNT(v.id) AS views_count
            FROM views_type v
            JOIN users u ON v.user_id = u.telegram_id
            GROUP BY u.id, u.user_name
            ORDER BY views_count DESC
            LIMIT 10;
        """
        curs.execute(query)
        results = curs.fetchall()
        curs.close()
        conn.close()

        # Форматируем вывод
        return [["@" + row[0], row[1]] for row in results]

    except Exception as e:
        print("Ошибка при получении топ-10 пользователей:", e)
        return []

# топ 10 по добавлению в избранное
def top_10_users_by_fav():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        query = """
            SELECT u.user_name, COUNT(v.id) AS fav_count
            FROM favorite_songs v
            JOIN users u ON v.telegram_id = u.telegram_id
            GROUP BY u.id, u.user_name
            ORDER BY fav_count DESC
            LIMIT 10;
        """
        curs.execute(query)
        results = curs.fetchall()
        curs.close()
        conn.close()

        # Форматируем вывод
        return [["@" + row[0], row[1]] for row in results]

    except Exception as e:
        print("Ошибка при получении топ-10 пользователей:", e)
        return []

# зарегистрировались сегодня
def get_users_registration_time_today():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()

        # Получаем сегодняшнюю дату
        today_date = date.today()

        # SQL-запрос: выбираем user_name и рег. время за сегодня
        query = """
            SELECT user_name, reg_time
            FROM users
            WHERE DATE(reg_time) = %s;
        """

        curs.execute(query, (today_date,))
        results = curs.fetchall()

        users_list = []

        for user_name, reg_time in results:
            # Вычисляем часы и минуты регистрации
            hours_minutes = reg_time.strftime("%H:%M")
            users_list.append(["@" +user_name, hours_minutes])

        curs.close()
        conn.close()

        return users_list

    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return []

# просмотренный контент сегодня
def get_user_actions_today():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()

        today_date = date.today()

        # Запрос для получения данных за сегодня
        query = """
            SELECT u.user_name, us.content_type, us.content_name, us.time
            FROM users_statistic us
            JOIN users u ON u.telegram_id = us.user_id
            WHERE DATE(us.time) = %s AND u.telegram_id != %s; 
        """

        curs.execute(query, (today_date,GENERAL_ADMIN))
        results = curs.fetchall()

        actions_list = []

        for idx, (user_name, content_type_num, content_name, action_time) in enumerate(results, start=1):
            # Замена типа контента на текст
            content_type_text = VIEWS_DICT.get(content_type_num, f'Тип {content_type_num}')

            # Вычисление времени просмотра в часах и минутах
            hours_minutes = action_time.strftime("%H:%M")

            # Формируем строку
            line = f"{idx}. @{user_name}    время: {hours_minutes} \n {content_type_text}   {content_name}\n\n"
            actions_list.append(line)

        curs.close()
        conn.close()

        return actions_list

    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return []
########################################################################################################################

# сбор статистики просмотра контента
def update_views(content_name, content_type):
    if content_name not in KEYBOARD_CALL:
        try:
            conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
            curs = conn.cursor()
            curs.execute("UPDATE views SET count_views = count_views + 1, time_update = NOW() WHERE content_name = %s AND content_type = %s;", (content_name, content_type))
            if curs.rowcount == 0:
                curs.execute("INSERT INTO views (content_name, content_type, count_views) VALUES (%s, %s, 1);", (content_name, content_type))
            conn.commit()
            curs.close()
            conn.close()
        except Exception as e:
            print("Ошибка при обновлении просмотров:", e)


# статистика просмотра статей за сегодня
def article_views_today():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        today_date = dt.datetime.now().date()
        curs.execute(
            "SELECT COUNT(*) FROM users_statistic WHERE user_id != '1422691786' AND content_type = 3 AND DATE(time) = %s",
            (today_date,)
        )
        result = curs.fetchall()
        curs.close()
        conn.close()
        if not result[0][0]:
            return 0
        else:
            return result[0][0]
    except:
        return 0


# статистика просмотра статей за месяц
def article_views_month():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        now = dt.datetime.now()
        current_year = now.year
        current_month = now.month

        start_of_month = dt.date(current_year, current_month, 1)
        if current_month == 12:
            next_month = dt.date(current_year + 1, 1, 1)
        else:
            next_month = dt.date(current_year, current_month + 1, 1)

        curs.execute(
            "SELECT COUNT(*) FROM users_statistic WHERE user_id != '1422691786' AND content_type = 3 AND time >= %s AND time < %s",
            (start_of_month, next_month)
        )
        result = curs.fetchall()
        curs.close()
        conn.close()
        if not result[0][0]:
            return 0
        else:
            return result[0][0]
    except:
        return 0


# статистика просмотра песен за сегодня
def song_views_today():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        today_date = dt.datetime.now().date()
        curs.execute(
            "SELECT COUNT(*) FROM users_statistic WHERE user_id != %s AND content_type IN (2, 5, 6) AND DATE(time) = %s",
            (GENERAL_ADMIN, today_date)
        )
        result = curs.fetchall()
        curs.close()
        conn.close()
        if not result[0][0]:
            return 0
        else:
            return result[0][0]
    except:
        return 0


# статистика просмотра песен за месяц
def song_views_month():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        now = dt.datetime.now()
        current_year = now.year
        current_month = now.month

        start_of_month = dt.date(current_year, current_month, 1)
        if current_month == 12:
            next_month = dt.date(current_year + 1, 1, 1)
        else:
            next_month = dt.date(current_year, current_month + 1, 1)

        curs.execute(
            "SELECT COUNT(*) FROM users_statistic WHERE user_id != %s AND content_type IN (2, 5, 6) AND time >= %s AND time < %s",
            (GENERAL_ADMIN,start_of_month, next_month)
        )
        result = curs.fetchall()
        curs.close()
        conn.close()
        if not result[0][0]:
            return 0
        else:
            return result[0][0]
    except:
        return 0

# статистика топ 10 песен

def get_top_10_songs():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        # Запрос для получения топ-10 песен по просмотрам
        curs.execute("""
            SELECT content_name, count_views
            FROM views
            WHERE content_type = 2
            ORDER BY count_views DESC
            LIMIT 10;
        """)
        results = curs.fetchall()
        curs.close()
        conn.close()
        # Возвращаем список списков: [имя песни, количество просмотров]
        return [[row[0], row[1]] for row in results]
    except Exception as e:
        print("Ошибка при получении топ-10 песен:", e)
        return []


# топ 10 в избранном
def get_top_10_songs_fav():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("""
            SELECT song_name, count(song_name)
            FROM favorite_songs
            GROUP BY song_name
            ORDER BY count(song_name) DESC
            LIMIT 10;
        """)
        results = curs.fetchall()
        curs.close()
        conn.close()
        # Возвращаем список списков: [имя песни, количество просмотров]
        return [[row[0], row[1]] for row in results]
    except Exception as e:
        print("Ошибка при получении топ-10 песен:", e)
        return []


####################################################################################
# СООБЩЕНИЯ
# сохраняем для каждого пользователя все приходящие и уходящие сообщения
def add_messages(telegram_id,message_id):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("INSERT INTO messages_id (telegram_id, message_id) VALUES (%s, %s);", (telegram_id, message_id))
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        print("Ошибка при обновлении сообщений:", e)


# удаляем сообщения пользователей
def delete_messages(telegram_id):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("DELETE FROM messages_id WHERE telegram_id =  %s", (telegram_id,))
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        print("Ошибка при удалении сообщений:", e)


# получаем все сообщения для пользователя
def select_messages_by_telegram_id(telegram_id):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute(f"SELECT message_id FROM messages_id WHERE telegram_id = %s", (telegram_id,))
    result1 = curs.fetchall()
    result = [t[0] for t in result1]
    curs.close()
    conn.close()
    return result

########################################################################################################################

# получаем список избранных треков для пользователя
def select_user_favorite_songs(telegram_id):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute(f"SELECT song_name FROM favorite_songs WHERE telegram_id = %s", (telegram_id,))
    result1 = curs.fetchall()
    result = [t[0] for t in result1]
    curs.close()
    conn.close()
    return result


# добавляем песню пользователя в избранное
def add_favorite_song_user(telegram_id,song):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("INSERT INTO favorite_songs (telegram_id, song_name) VALUES (%s, %s);", (telegram_id, song))
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        print("Ошибка при при добавлении песни:", e)


# удаляем песню пользователя из избранное
def delete_favorite_song_user(telegram_id,song):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("DELETE FROM favorite_songs WHERE telegram_id =  %s AND song_name = %s", (telegram_id, song))
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        print("Ошибка при удалении песни:", e)



# удаляем действия админов группы
def delete_admin_makers():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        for admin in ADMIN_ID:
            curs.execute("DELETE FROM users_statistic WHERE user_id =  %s", (admin,))
            curs.execute("DELETE FROM user_question_review  WHERE telegram_id =  %s", (admin,))
            curs.execute("DELETE FROM user_query  WHERE telegram_id =  %s", (admin,))

        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        print("Ошибка при удалении песни:", e)


# проверка есть ли трек у пользователя в избранном
def search_favorite_song_in_user_list(song,telegram_id):
    if len(song) < 33:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute(f"SELECT * FROM favorite_songs WHERE song_name = %s AND telegram_id = %s", (song,telegram_id,))
        result1 = curs.fetchall()
        result = [t[2] for t in result1]
        curs.close()
        conn.close()

    else:
        prefix = song[:30]
        suffix = song[-1]

        # Экранируем специальные символы
        escaped_prefix = escape_regex_string(prefix)
        escaped_suffix = escape_regex_string(suffix)

        # Конструируем регулярное выражение
        pattern = f"^{escaped_prefix}.*{escaped_suffix}$"

        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()

        query = "SELECT * FROM favorite_songs WHERE song_name ~ %s AND telegram_id = %s"
        curs.execute(query, (pattern,telegram_id))

        result = curs.fetchone()
        curs.close()
        conn.close()

    if result:
        return True
    else:
        return False

# получаем количество статей
def select_count_articles():
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute("SELECT COUNT(*) FROM articles")
    result = curs.fetchall()[0][0]
    curs.close()
    conn.close()
    return result


# текстовый поиск песен
########################################################################################################################
# Функция для нормализации строки: заменяет 'ё' на 'е', переводит в нижний регистр и убирает знаки препинания

def normalize_string(s):
    s = s.lower().replace('ё', 'е')
    words = s.split()
    result_words = []

    for word in words:
        # Проверяем, есть ли внутри дефис
        if '-' in word:
            cleaned = ''.join(c for c in word if c.isalnum() or c == '-')
            cleaned = cleaned.strip('-')
            if cleaned:  # если после очистки осталась непустая строка
                result_words.append(cleaned)
        else:
            cleaned = ''.join(c for c in word if c.isalnum())
            if cleaned:
                result_words.append(cleaned)

    return ' '.join(result_words)


# Функция для получения списка слов из строки
def get_words(s):
    words = s.split()
    return words


# Основная функция поиска
def select_search_text(query_text):
    # Подключение к базе данных
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()

    original_query = query_text.strip()
    normalized_query = normalize_string(original_query)
    query_words = get_words(normalized_query)

    results = set()

    def sort_song(results):
        matched_partial = []
        matched_full = []

        for result in results:
            words = get_words(result)
            # Проверка на полное совпадение (все слова из query_words есть в words)
            full_match = True
            for word in query_words:
                # Проверяем, есть ли слово или его часть в списке слов результата
                if not any(
                        song_word.lower() == word.lower() or song_word.lower().split('_')[0] == word.lower()
                        for song_word in words
                ):
                    full_match = False
                    break  # Если хоть одно слово не найдено, полный матч невозможен

            if full_match:
                matched_full.append(result)

            # Проверка на частичное совпадение (хотя бы одно слово)
            for word in query_words:
                if any(
                        song_word.lower() == word.lower() or song_word.lower().split('_')[0] == word.lower()
                        for song_word in words
                ):
                    matched_partial.append(result)
                    break  # переходим к следующему результату после первого совпадения

        if matched_full:
            return matched_full
        else:
            return matched_partial

    def remove_duplicates(lst):
        seen = set()
        result = []
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    def execute_exact_word_match(words_list):
        """Ищет строки, где все слова из списка встречаются точно в строке."""
        if not words_list:
            return
        conditions = []
        params = []
        for word in words_list:
            conditions.append("LOWER(REPLACE(REPLACE(text_field, 'ё', 'е'), ' ', '')) LIKE %s")
            params.append(f"%{word}%")

        pattern = r'\b' + r'\b.*\b'.join(words_list) + r'\b'
        pattern = pattern.replace(r'\b', r'\\b')  # экранирование

        query_str_group = """
            SELECT band FROM songs WHERE LOWER(REPLACE(REPLACE(band, 'ё', 'е'), ' ', '')) ~* %s
            UNION
            SELECT song_name FROM songs WHERE LOWER(REPLACE(REPLACE(song_name, 'ё', 'е'), ' ', '')) ~* %s
        """
        curs.execute(query_str_group, (pattern, pattern))
        for r in curs.fetchall():
            results.add(r[0] if r[0] else r[1])


    def execute_full_phrase():
        """Ищет полную фразу."""
        pattern = normalized_query.replace(' ', r'\s+')
        regex_pattern = r'\b' + pattern + r'\b'
        query_str_full = """
            SELECT band FROM songs WHERE LOWER(REPLACE(REPLACE(band, 'ё', 'е'), ' ', '')) ~* %s
            UNION
            SELECT song_name FROM songs WHERE LOWER(REPLACE(REPLACE(song_name, 'ё', 'е'), ' ', '')) ~* %s
        """
        curs.execute(query_str_full, (regex_pattern, regex_pattern))
        for r in curs.fetchall():
            results.add(r[0] if r[0] else r[1])


    def execute_search(words_list):
        """Ищет строки содержащие все слова из списка."""
        if not words_list:
            return
        conditions_band = []
        conditions_song = []
        params = []
        for word in words_list:
            cond_band = "LOWER(REPLACE(REPLACE(band, 'ё', 'е'), ' ', '')) LIKE %s"
            cond_song = "LOWER(REPLACE(REPLACE(song_name, 'ё', 'е'), ' ', '')) LIKE %s"
            param_word = f"%{word}%"
            conditions_band.append(cond_band)
            conditions_song.append(cond_song)
            params.extend([param_word] * 2)

        query_str_band = f"""
            SELECT song_name FROM songs WHERE {' AND '.join(conditions_band)}
        """
        query_str_song = f"""
            SELECT song_name FROM songs WHERE {' AND '.join(conditions_song)}
        """

        curs.execute(query_str_band, params[:len(conditions_band)])
        for r in curs.fetchall():
            results.add(r[0])

        curs.execute(query_str_song, params[len(conditions_band):])
        for r in curs.fetchall():
            results.add(r[0])

    def filter_and_sort(items, term):
        term_lower = term.lower()
        # списки для совпадений и остальных
        exact_matches = []
        others = []

        for item in items:
            if ' - ' in item:
                prefix, rest = item.split(' - ', 1)
                prefix_lower = prefix.lower()

                # Полное совпадение первой части с поисковым термином
                if prefix_lower == term_lower:
                    exact_matches.append(item)
                else:
                    others.append(item)
            else:
                others.append(item)

        # Сортируем только список точных совпадений по алфавиту без учёта регистра
        exact_matches_sorted = sorted(exact_matches, key=lambda x: x.lower())

        # Остальные оставляем в исходном порядке или сортируем по желанию
        # Например, отсортировать их тоже по алфавиту:
        others_sorted = sorted(others, key=lambda x: x.lower())

        return exact_matches_sorted + others_sorted



    # 1. Попытка поиска всей фразы целиком
    execute_full_phrase()
    if results:
        curs.close()
        conn.close()
        # results = sorted(results, key=str.lower)
        results = remove_duplicates(sort_song(list(results)))
        return filter_and_sort(results,query_text)


    # 2. Попытка поиска по отдельным словам (отдельно)
    execute_search(query_words)
    if results:
        curs.close()
        conn.close()
        # results = sorted(results, key=str.lower)
        results = remove_duplicates(sort_song(list(results)))
        return filter_and_sort(results, query_text)

    # 3. Удаление слов по одному с начала и с конца и повторный поиск
    for i in range(len(query_words) - 1, 0, -1):
        # Удаляем i слов с начала
        sub_words_start = query_words[i:]
        execute_search(sub_words_start)
        if results:
            break
        # Удаляем i слов с конца
        sub_words_end = query_words[:len(query_words) - i]
        execute_search(sub_words_end)
        if results:
            break

    curs.close()
    conn.close()
    # results = sorted(results, key=str.lower)
    results = remove_duplicates(sort_song(list(results)))
    return filter_and_sort(results, query_text)

########################################################################################################################
# Аккорды
# аккорды по типу
def select_chord_type(type):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute(f"SELECT id,chord FROM chords WHERE type_id = %s ORDER BY id ASC", (type,))
    result = curs.fetchall()
    result = [t[1] for t in result]
    curs.close()
    conn.close()
    return result


########################################################################################################################

# ошибка загрузки песни
def fix_error(type,song,error):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("INSERT INTO errors (type,song, description) VALUES (%s, %s, %s);", (type, song, error))
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        print("Ошибка при при добавлении лога:", e)


# добавляем отзыв или вопрос пользователя
def add_qw_user(type,qr,user_name,telegram_id):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("INSERT INTO user_question_review (type,qr,user_name,telegram_id) VALUES (%s, %s,%s, %s);", (type,qr,user_name,telegram_id))
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        print("Ошибка при при добавлении песни:", e)


# поиск пользователя по нику
def select_search_user(user_name):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("SELECT telegram_id FROM users WHERE user_name = %s", (user_name,))
        user = curs.fetchone()[0]
        curs.close()
        conn.close()
        return user
    except Exception as err:
        print(f'Пользователь {user_name} не найден!')
        return None

# поиски пользователя
def add_user_query(type,query,telegram_id):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("INSERT INTO user_query (type,query,telegram_id) VALUES (%s, %s,%s);", (type,query,telegram_id))
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        print("Ошибка при при добавлении песни:", e)


# вывод всех песен группы
def select_all_songs(band):
    modified_text = re.sub(r'[-,\s]+', '%', band)
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute("SELECT song_name,song_chord,song_link FROM songs WHERE band ILIKE %s", (f"%{modified_text}%",))
    result = curs.fetchall()
    result = [[t[0],t[1],[2]] for t in result]
    curs.close()
    conn.close()
    return result


def select_all_songs_by_name():
    # получаем список всех песен
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute("SELECT song_name FROM songs")
    result = [song[0] for song in curs.fetchall()]
    curs.close()
    conn.close()
    return result


# получение всех песен и всех групп из бд в датафреймах
def select_all_songs_and_all_band():
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    # получаем список групп
    curs.execute("SELECT letter,band FROM bands")
    result1 = curs.fetchall()
    column_names = [elt[0] for elt in curs.description]
    df1 = pd.DataFrame(result1, columns=column_names)

    # получаем список всех песен
    curs.execute("SELECT band,song_name,song_chord,song_link, video_link FROM songs")
    result2 = curs.fetchall()
    column_names = [elt[0] for elt in curs.description]
    df2 = pd.DataFrame(result2, columns=column_names)
    curs.close()
    conn.close()
    return df1, df2


# Поиск видеоссылки на песню
def select_search_video_link(song):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    if len(song) > 32:
        prefix = song[:30]
        suffix = song[-1]
        # Экранируем специальные символы
        escaped_prefix = escape_regex_string(prefix)
        escaped_suffix = escape_regex_string(suffix)
        # Конструируем регулярное выражение
        pattern = f"^{escaped_prefix}.*{escaped_suffix}$"
        query = "SELECT video_link FROM songs WHERE song_name ~ %s"
        curs.execute(query, (pattern,))
        result = curs.fetchone()
    else:
        curs.execute(f"SELECT video_link FROM songs WHERE song_name = %s", (song,))
        result = curs.fetchone()
    curs.close()
    conn.close()
    return result[0]

########################################################################################################################
# для хранения рассылок

def add_send_mess(content_name,user_id,message_id,type_cont):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("INSERT INTO sends_messages (content_name,user_id,message_id,type) VALUES (%s, %s,%s, %s);", (content_name,user_id,message_id,type_cont))
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        print("Ошибка при при добавлении сообщения:", e)

# список рассылок для удаления
def select_all_send():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("SELECT DISTINCT content_name FROM sends_messages ")
        result = curs.fetchall()
        result = [[result.index(elt),elt[0]] for elt in result]
        curs.close()
        conn.close()
        return result
    except Exception as e:
        print("Ошибка:", e)


 # список сообщений и пользователей рассылки
def select_user_mess_send(content_name):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("SELECT user_id,message_id FROM sends_messages WHERE content_name = %s",(content_name,))
        result = curs.fetchall()
        result = [[elt[0],elt[1]] for elt in result]
        curs.close()
        conn.close()
        return result
    except Exception as e:
        print("Ошибка при при добавлении сообщения:", e)


def delete_mess_sends(content_name):
    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()
    curs.execute("DELETE FROM sends_messages WHERE content_name = %s", (content_name,))
    conn.commit()
    curs.close()
    conn.close()

########################################################################################################################
# Убираем из избранного треки которые удалены
# обновление списка избранное
# получаем список избранных треков для всех
def update_user_favorite_songs():

    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()

    # Получаем список песен из таблицы favorite_songs
    curs.execute("SELECT song_name FROM favorite_songs")
    result1 = curs.fetchall()
    songs_list = [t[0] for t in result1]

    if not songs_list:
        # Если список пустой, возвращаем пустой список
        curs.close()
        conn.close()
        return []

    # Создаем строку с плейсхолдерами для IN-запроса
    placeholders = ','.join(['%s'] * len(songs_list))
    query = f"SELECT song_name FROM songs WHERE song_name IN ({placeholders})"

    # Выполняем запрос с передачей параметров
    curs.execute(query, songs_list)
    existing_songs = set(row[0] for row in curs.fetchall())

    missing_songs = [song for song in songs_list if song not in existing_songs]

    if missing_songs:
        # Удаляем пропущенные песни из favorite_songs
        delete_placeholders = ','.join(['%s'] * len(missing_songs))
        delete_query = f"DELETE FROM favorite_songs WHERE song_name IN ({delete_placeholders})"
        curs.execute(delete_query, missing_songs)
        conn.commit()

    curs.close()
    conn.close()

    return missing_songs


# Удаление песни
########################################################################################################################
# Удаление песни из базы и каталога
def dell_song(song):
    if len(song) > 30:
        result = select_long_chord_song_info(song)
    else:
        result = select_chord_song_info(song)

    band_name = result[1]
    song_name = result[2]
    song_root = os.path.dirname(result[4])
    song_link = result[4]
    print(song_name,song_link,song_root)

    conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
    curs = conn.cursor()

    curs.execute("DELETE FROM songs WHERE song_name =  %s", (song_name,))
    curs.execute("DELETE FROM favorite_songs WHERE song_name =  %s", (song_name,))
    curs.execute("DELETE FROM errors WHERE song =  %s", (song_name,))
    curs.execute("DELETE FROM views WHERE content_name =  %s", (song_name,))
    curs.execute("DELETE FROM users_statistic WHERE content_name =  %s", (song_name,))


    # удаляем физически файл
    try:
        os.remove(song_link)
        print("Файл успешно удалён")
    except FileNotFoundError:
        print("Файл не найден")
    except Exception as e:
        print(f"Ошибка при удалении файла: {e}")

    # Проверяем, пуста ли папки и удаляем если пуста
    if os.path.exists(song_root) and os.path.isdir(song_root):
        # Получаем список файлов и папок внутри
        contents = os.listdir(song_root)
        # Проверяем, пустая ли папка
        if not contents:
            try:
                os.rmdir(song_root)
                curs.execute("DELETE FROM bands WHERE band =  %s", (band_name,))
                print(f"Папка '{song_root}' успешно удалена.")
            except Exception as e:
                print(f"Ошибка при удалении папки: {e}")
        else:
            print(f"В папке '{song_root}' ещё есть файлы или папки.")
    else:
        print(f"Папка '{song_root}' не существует.")

    conn.commit()
    curs.close()
    conn.close()
    return result

# редактирование имён в базе и песнях
########################################################################################################################
# Редактирование имён песен
def get_unique_filename(directory, filename):
    print(directory, filename, sep=' проверка уникальности ')
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{name}_{counter}{ext}"
        counter += 1
    print('Новое уникальное имя', new_filename)
    return new_filename


def rename_song(song, song_new_name):
    try:
        if len(song) > 33:
            result = select_long_chord_song_info(song)
        else:
            result = select_chord_song_info(song)

        band_name = result[1]
        song_name = result[2]
        song_root = os.path.dirname(result[4])
        song_chord = result[3]
        song_link = result[4]
    except:
        return '❌ Песня не найдена в базе!'

    for inf in [band_name,song_name, song_link, song_chord]:
        print(inf)

    # новые данные для переименования
    if ' - ' in song_new_name:
        band_new_name = song_new_name.split(' - ')[0]
        # Формируем новые пути
        if song_new_name[0].upper().isdigit():
            letter_root = '0-9'
        else:
            letter_root = song_new_name[0].upper()
        song_new_root = f'scr/songs/{letter_root}/{band_new_name}'
        # Формируем предполагаемый новый путь файла

        song_new_name = song_new_name + '.txt'
        base_name = os.path.basename(song_new_name)
        # Получаем имя файла без расширения
        filename_without_ext, ext = os.path.splitext(base_name)


        # Проверяем уникальность имени файла
        unique_filename = get_unique_filename(
            os.path.join(song_new_root),
            base_name
        )
        print('уникальное имя',unique_filename)
        song_new_name = unique_filename
        new_song = unique_filename.replace('.txt','')


        song_new_link = os.path.join(
            'scr',
            'songs',
            letter_root,
            band_new_name,
            song_new_name
        )
        print('путь к новому файлу',song_new_link)
        # Предполагаемый путь для перемещения файла
        destination_dir = os.path.join('scr', 'songs', letter_root, band_new_name)
        print(destination_dir,'имя файла: ',song_new_name)

        if not os.path.exists(song_link):
            print('Файл не найден по пути:', song_link)

        try:
            # проверяем наличие папки и создаём если нужно
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)

            # Перемещаем файл с проверкой уникальности имени
            shutil.move(song_link, os.path.join(destination_dir, unique_filename))

            # удаляем старую папку если она пуста
            if not os.listdir(song_root):
                os.rmdir(song_root)

            print(f"Файл успешно перемещён и переименован в: {os.path.join(destination_dir, unique_filename)}")

            # Обновляем путь к файлу после перемещения
            moved_file_path = os.path.join(destination_dir, unique_filename)

            # перезаписываем первую строку файла

            with open(song_new_link, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            lines[0] = new_song + '\n\n'

            with open(song_new_link, 'w', encoding='utf-8') as file:
                file.writelines(lines)

            try:
                conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
                curs = conn.cursor()

                old_data = len(select_song(band_name))
                new_data = len(select_song(band_new_name))
                print(old_data,new_data)


                if old_data == 1 and new_data > 0: # если песня одна переименовываем группу в базе
                    # старая 1 и новая уже есть удаляем старую
                    if not select_song(band_new_name):
                        curs.execute("DELETE FROM band WHERE band =  %s", (band_name,))



                elif old_data == 1 and new_data == 0:
                    # старая одна и новой нет то переименуем старую
                    curs.execute(
                        "UPDATE bands SET letter = %s,  band = %s WHERE band = %s",
                        (letter_root,band_new_name,band_name)) # обновляем имя старой группы



                elif old_data > 1 and new_data == 0:
                    curs.execute(" INSERT INTO bands (letter, band) VALUES (%s, %s) ON CONFLICT (band) DO NOTHING",
                                 (letter_root, band_new_name))

                elif old_data > 1 and new_data > 0:
                    pass

                curs.execute(
                    "UPDATE songs SET band = %s, song_name = %s, song_chord = %s, song_link = %s WHERE song_name = %s",
                    (band_new_name,new_song, song_chord,song_new_link,song_name))

                curs.execute(
                    "UPDATE favorite_songs SET song_name = %s WHERE song_name = %s",
                    (new_song,song_name))

                curs.execute(
                    "UPDATE users_statistic SET content_name = %s WHERE content_name = %s",
                    (new_song, song_name))

                curs.execute(
                    "UPDATE views SET content_name = %s WHERE content_name = %s",
                    (new_song, song_name))

                conn.commit()
                curs.close()
                conn.close()
            except Exception as e:
                print(e)
                return '❌ Не удалось перезаписать песню в базу данных!'

            return f'✅ Песня успешно переименована и перезаписана!\n\nСтарое название: {song_name}\nНовое название: {new_song}'

        except Exception as e:
            print(f"Ошибка при перемещении файла: {e}")
            return '❌ Ошибка перемещения песни!'

    else:
        return '❌ Ошибка в новом имени песни!'

########################################################################################################################
# Добавляем новый контент
def add_new_content(file_link):
    #1 получаем данные нового контента
    song_link = file_link
    filename_with_ext = os.path.basename(file_link)
    song_new_name = os.path.splitext(filename_with_ext)[0]

    with open(file_link, 'r', encoding='utf-8') as file:
        for line in file:
            if "Аккорды" in line:
                match = re.search(r'Аккорды', line)
                if match:
                    chord_song = line.replace('Аккорды(','')
                    chord_song = chord_song.split(')', 1)[0]
                    break  # если нужно только первое вхождение


    if ' - ' in song_new_name:
        band_new_name = song_new_name.split(' - ')[0]
        # Формируем новые пути
        if song_new_name[0].upper().isdigit():
            letter_root = '0-9'
        elif song_new_name[0].upper() in ['#','.','$','(','+','-','=',"'",':']:
            letter_root = '0-9'
        else:
            letter_root = song_new_name[0].upper()
        song_new_root = f'scr/songs/{letter_root}/{band_new_name}'
        # Формируем предполагаемый новый путь файла

        song_new_name = song_new_name + '.txt'
        base_name = os.path.basename(song_new_name)
        # Получаем имя файла без расширения
        filename_without_ext, ext = os.path.splitext(base_name)

        # Проверяем уникальность имени файла
        unique_filename = get_unique_filename(
            os.path.join(song_new_root),
            base_name
        )
        print('уникальное имя',unique_filename)
        song_new_name = unique_filename
        new_song = unique_filename.replace('.txt','')


        song_new_link = os.path.join(
            'scr',
            'songs',
            letter_root,
            band_new_name,
            song_new_name
        )
        print('путь к новому файлу',song_new_link)
        # Предполагаемый путь для перемещения файла
        destination_dir = os.path.join('scr', 'songs', letter_root, band_new_name)
        print(destination_dir,'имя файла: ',song_new_name)

        if not os.path.exists(song_link):
            print('Файл не найден по пути:', song_link)

        try:
            # проверяем наличие папки и создаём если нужно
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)

            # Перемещаем файл с проверкой уникальности имени
            shutil.move(song_link, os.path.join(destination_dir, unique_filename))
            print(f"Файл успешно перемещён и переименован в: {os.path.join(destination_dir, unique_filename)}")
            # Обновляем путь к файлу после перемещения
            moved_file_path = os.path.join(destination_dir, unique_filename)

            # перезаписываем первую строку файла

            with open(song_new_link, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            lines[0] = new_song + '\n'

            with open(song_new_link, 'w', encoding='utf-8') as file:
                file.writelines(lines)

        except Exception as e:
            print(e)
            return '❌ Не удалось записать песню в папку!'


        # 2 Проверяем есть ли такая группа в базе если нет то записываем группу в базу
        try:
            conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
            curs = conn.cursor()
            if not select_song(band_new_name):
                curs.execute(" INSERT INTO bands (letter, band) VALUES (%s, %s) ON CONFLICT (band) DO NOTHING",
                         (letter_root, band_new_name))
            curs.execute(
                "INSERT INTO songs (band, song_name, song_chord, song_link,content_type) VALUES (%s, %s,%s, %s,%s)",
                (band_new_name, new_song, chord_song, song_new_link, 2))

            conn.commit()
            curs.close()
            conn.close()
            return f'✅ Песня {new_song} успешно  записана!'
        except Exception as e:
            print(DBNAME)
            print(f' Ошибка записи группы или песни - {e}')
            return '❌ Не удалось записать песню в базу данных!'


# добавляем клик по партнёрской ссылке
def add_user_click(telegram_id, user_nick, site_name):
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        insert_query = """
           INSERT INTO clicks (telegram_id, user_nick, site_name)
           VALUES (%s, %s, %s);
           """
        curs.execute(insert_query, (telegram_id, user_nick, site_name))
        conn.commit()
        curs.close()
        conn.close()

    except Exception as e:
        print(f"Ошибка при записи в базу: {e}")


def get_info_about_partner_links():
    try:
        conn = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
        curs = conn.cursor()
        curs.execute("SELECT * FROM clicks")
        results = curs.fetchall()
        curs.close()
        conn.close()

        data = defaultdict(list)
        for row in results:
            # row = (id, user_id, nick, site, datetime)
            site = row[3]
            nick = row[2]
            dt = row[4].strftime('%Y.%m.%d')  # форматируем дату

            data[site].append([nick, dt])

        return dict(data)

    except Exception as e:
        print(f"Ошибка при записи в базу: {e}")
        return {}


if __name__ == "__main__":
    print(select_user_list())







