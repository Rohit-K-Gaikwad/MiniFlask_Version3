"""

GET
POST
DELETE
PATCH
PUT
"""

import json
from flask import Blueprint, request, Response
from dal.dml import fetch_resource, insert_resource, __delete_resource, upsert_films
from models.datamodels.characters import Character_
from models.datamodels.films import Film_
from pydantic import parse_obj_as, error_wrappers
from pydantic.error_wrappers import ValidationError


from pydantic import BaseModel, validator
from typing import Union, Optional


class PostFilmResponse(BaseModel):
    """
      response_obj = {
        "records_count": result,
        "film_name": film_data.title,
        "message": msg
    }
    """

    records_count: Union[int, str]
    film_name: Optional[str]
    message: str

    @validator("records_count")
    def check_records_count(cls, records_count):
        if isinstance(records_count, int) or isinstance(records_count, str):
            return int(records_count)


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
    """
        {
      "title": "A New Hope",
      "episode_id": 99991111,
      "opening_crawl": "random",
      "director": "George Lucas",
      "producer": "Gary Kurtz, Rick McCallum",
      "release_date": "1977-05-25",
      "created": "2014-12-10T14:23:31.880000Z",
      "edited": "2014-12-20T19:49:45.256000Z",
      "url": "https://swapi.dev/api/films/1/"
    }
    :return:
    """

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

    # response validation
    PostFilmResponse(**response_obj)

    return Response(
        json.dumps(response_obj),
        status=201,
        mimetype="application/json"
    )


@starwar_app.route("/films", methods=["DELETE"])
def delete_films():
    """
     https://127.0.0.1:8080/films/1  (path param)
     https://127.0.0.1:8080/films?film_id=1  (query param)

    Returns:

    """

    # how to capture query parameters?
    film_id = int(request.args.get("film_id"))
    result = __delete_resource("starwarsDB.film", "film_id", film_id)
    if result == 0:
        response_obj = {
            "ERROR": f"no records to delete against film_id - {film_id}"
        }
        return Response(
            json.dumps(response_obj),
            status=409,
            mimetype="application/json"
        )
    response_obj = {
        "message": f"record against film_id - {film_id} deleted successfully"
    }
    return Response(
        json.dumps(response_obj),
        status=200,
        mimetype="application/json"
    )


@starwar_app.route("/films", methods=["PUT"])
def put_films():
    """

    HTTP PUT -  http://127.0.0.1:5000/starwars/films

    payload -

    {
      "title": "A New Hope - RANDOM",
      "episode_id": 4,
      "opening_crawl": "random",
      "director": "George Lucas",
      "producer": "Gary Kurtz, Rick McCallum",
      "release_date": "1977-05-25",
      "created": "2014-12-10T14:23:31.880000Z",
      "edited": "2014-12-20T19:49:45.256000Z",
      "url": "https://swapi.dev/api/films/1/"
    }

    Returns:

    """

    # how to capture request body/ request payload/ request data?
    request_data = request.json

    # request validation
    try:
        film_data = Film_(**request_data)
    except ValidationError as ex:
        return Response(
            json.dumps({"message": "bad request"}),
            status=400,
            mimetype="application/json"
        )

    home_url = "https://swapi.dev"
    relative_url = "/api/film/{num_}"  # magic string
    absolute_url = home_url + relative_url.format(num_=film_data.episode_id)
    result = upsert_films(film_data, absolute_url)
    if result:
        msg = "New record created successfully"
    else:
        msg = "existing record has been updated"

    response_obj = {
        "records_count": result,
        "film_name": film_data.title,
        "message": msg
    }
    return Response(
        json.dumps(response_obj),
        status=200,
        mimetype="application/json"
    )












