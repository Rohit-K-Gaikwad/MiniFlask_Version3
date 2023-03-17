"""

GET
POST
DELETE
PATCH
PUT
"""

import json
from flask import Blueprint, request, Response
from dal.dml import fetch_resource, insert_resource
from models.datamodels.characters import Character_
from models.datamodels.films import Film_
from pydantic import parse_obj_as, error_wrappers



# Blueprit class instantiation
starwar_app = Blueprint("starwars", __name__, url_prefix="/starwars")


@starwar_app.get("/welcome")
def welcome():
    return "hello world from starwars sub-application"


# @starwar_app.route("/people", methods=["GET", "POST", "DELETE", "PATCH"])
# def get_characters():
#     if request.method == "GET":
#         # write fetch resource logic here
#     elif request.method == "POST":
#         # write logic to create new record on server


@starwar_app.route("/people", methods=["GET"])
def get_characters():
    data = fetch_resource("people")
    characters = data.get("results")
    characters = parse_obj_as(list(characters), Character_)
    response = {
        "count": data.get("count"),
        "message": "successful"
    }
    return Response(response, status=200, mimetype="application/json")


@starwar_app.route("/films", methods=["POST"])
def post_films():

    request_data = request.json
    # request body validation
    try:
        film_data = Film_(**request_data)
    except error_wrappers.ValidationError as ex:
        response_obj = {
            "message": f"{ex}"
        }
        return Response(
            json.dumps(response_obj),
            status=422,
            mimetype="application/json"
        )

    film_columns = [
        "title",
        "opening_crawl",
        "director",
        "producer",
        "release_date",
        "created",
        "edited",
        "url",
    ]

    film_values = [
        film_data.title,
        film_data.opening_crawl,
        film_data.director,
        film_data.producer,
        film_data.release_date,
        film_data.created.strftime("%y-%m-%d"),
        film_data.edited.strftime("%y-%m-%d"),
        film_data.url,
    ]

    result = insert_resource(
        "film", "film_id", film_data.episode_id, film_columns, film_values
    )

    msg = None
    if result:
        msg = "record created successfully"
    else:
        response_obj = {
            "message": "failed to insert record"
        }
        return Response(
            json.dumps(response_obj),
            status=409,
            mimetype="application/json"
        )

    response_obj = {
        "records_count": result,
        "film_name": film_data.title,
        "message": msg
    }
    return Response(
        json.dumps(response_obj),
        status=201,
        mimetype="application/json"
    )







