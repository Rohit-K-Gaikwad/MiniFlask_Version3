"""
DML stands for Data Manipulation Language

This module contains generic functions to insert data into sql tables
"""
import pymysql
import requests
from dal.db_conn_helper import get_db_conn
from typing import List, Union
from pymysql.err import IntegrityError


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






if __name__ == "__main__":
    insert_resource("characters", "char_id", 1,
                    ["name", "height"], ["prashant", "176"])
