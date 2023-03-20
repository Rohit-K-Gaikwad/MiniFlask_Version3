"""
DML stands for Data Manipulation Language

This module contains generic functions to insert data into sql tables
"""
import pymysql
import requests
import logging
from dal.db_conn_helper import get_db_conn
from typing import List, Union, Dict, Optional
from pymysql.err import IntegrityError
from collections import OrderedDict


def insert_resource(
    table_name: str, primary_key_: str, primary_value: int, columns_: List, values: List
):
    """
    Inserts a record in the database using primary key

    Args:
        table_name (str):
        primary_key_ (str):
        primary_value (int):
        columns_ (list):
        values (list):

    Returns:
        number of records inserted in DB table
    """

    column_names = ", ".join(columns_)
    value_fields = ", ".join(values)

    column_names.rstrip(", ")
    value_fields.rstrip(", ")

    value_fields = ""
    for value in values:
        if isinstance(value, str):
            value_fields = value_fields + '''"''' + value + '''"''' + """, """
        elif isinstance(value, int):
            value_fields = value_fields + str(value) + ""","""

    value_fields = value_fields.rstrip(""", """)

    result = None
    with get_db_conn() as conn:
        cursor = conn.cursor()

        sql_magic = f"""insert into 
        starwarsDB.{table_name} ({primary_key_}, {column_names}) 
        values ({primary_value}, {value_fields});"""
        try:
            result = cursor.execute(sql_magic)
            conn.commit()
        except IntegrityError as ex:
            print(f"[ ERROR ] record already exists - {ex}")
            pass
    return result


def fetch_resource(resource):
    resource_url = "https://swapi.dev/api/" + resource
    response = requests.get(resource_url)
    data = response.json()
    return data


def __delete_resource(
        table_name: str,
        primary_key: str,
        primary_val: Union[str, int]):
    """
    function deletes records based on primary key

    Args:
        table_name:
        primary_key:
        primary_val:

    Returns:

    """

    try:
        with get_db_conn() as conn:
            cursor = conn.cursor()
            sql_magic = f"delete from {table_name} where {primary_key}={primary_val}"
            data = cursor.execute(sql_magic)
            conn.commit()
        return data
    except pymysql.Error as ex:
        print(f"[ ERROR ] details - {ex}")
        return 0


def build_upsert_sql_query(
    table_name, commands, prime_key, prime_value, clause, keys_, values_
) -> str:
    """Builds sql query based on input.
    Args:
        table_name (str): table under consideration for sql query.
        commands (str): sql commands such as select, insert, update etc.
        prime_key (str): primary key for particular table.
        prime_value(int, str): value to be updated for primary key
        clause (str): clauses to filter results.
        keys_ (list): list of keys query refers to.
        values_ (list): list of values query stores (required for insert and update statements.)
    Returns:
        query (str): complete sql query
    """

    if prime_key in keys_:
        keys_.remove(prime_key)
    keys_literals = ", ".join(keys_)

    mid_literals = []

    if int(prime_value) in values_:
        values_.remove(int(prime_value))

    for i in range(len(values_)):
        mid = '''"''' + str(values_[i]) + '''"'''
        mid_literals.append(mid)

    values_literals = ", ".join(mid_literals)

    mid_update_literals = []
    for key_lit, val_lit in zip(keys_, mid_literals):
        mid = """ , """ + key_lit + """=""" + val_lit
        mid_update_literals.append(mid)

    update_literals = "".join(mid_update_literals)

    # skipping first
    update_literals = update_literals[3:]

    sql = (
        r"{} {}"
        r"({}, {}) "
        r"VALUES({}, {})"
        r" {} {};"
        r"".format(
            commands,
            table_name,
            prime_key,
            keys_literals,
            int(prime_value),
            values_literals,
            clause,
            update_literals,
        )
    )

    return sql


def get_url_ids(urls) -> str:
    """retrieves id part of singular record urls such as -
     `https://swapi.co/api/characters/2/`
    Args:
        urls (list): list of urls
    Returns:
        str: space delimited string having ids from all urls.
    """
    ids = []
    for url in urls:
        ids.append(url.split("/")[-1])
    return " ".join(ids)


def upsert_films(film: Dict, endpoint: str) -> Optional[int]:
    """
    Notes

    upsert = update + insert

    "swapi.dev/api/films/1


    Inserts values into `films` table, updates on duplicate key.
    Args:
        film (dict):
        endpoint (str):
    Returns:
    """

    connection = get_db_conn()

    # retrieving keys and values from an OrderedDict into list
    # so as to maintain relative order
    film = OrderedDict(film)
    film_id = int(get_url_ids([endpoint]))
    keys_ = []
    values_ = []
    for key_, val_ in film.items():
        keys_.append(key_)
        if isinstance(val_, list):
            values_.append(get_url_ids(val_))
        else:
            values_.append(val_)

    # importing inside the function to avoid `circular imports` issue.
    from models.datamodels.films import Film_
    from pydantic.error_wrappers import ValidationError

    # data validation layer using pydantic model.
    # If endpoint yields no result then return.

    try:
        if film is not OrderedDict([("detail", "Not found")]):  # Iterable: to determine whether an object is iterable
            Film_(**film)                                                  # is to call iter(obj).

        else:
            print(f"\n\n[ WARNING ] Endpoint - {endpoint} - yields nothing!!")
            return None
    except ValidationError as ve:
        print(
            f"[ Error ] fetched film record does not meet validations. "
            f"Perhaps, type conversions required. More details on error  - {ve}"
        )

    try:
        with connection.cursor() as cursor:

            sql = build_upsert_sql_query(
                "starwarsDB.film",
                "INSERT INTO",
                "film_id",
                film_id,
                "ON DUPLICATE KEY UPDATE",
                keys_,
                values_,
            )

            print(f"\n see here the SQL query :: \n\n{sql}")

            result = cursor.execute(sql)
            connection.commit()
    except pymysql.Error as ex:
        logging.error(f"ERROR. Details - {ex}")
        return 0
    finally:
        connection.close()

    return result


if __name__ == "__main__":
    insert_resource("characters", "char_id", 1,
                    ["name", "height"], ["prashant", "176"])
