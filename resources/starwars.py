"""

GET
POST
DELETE
PATCH
PUT
"""

from flask import Blueprint, request, Response
from dal.dml import fetch_resource
from models.datamodels.characters import Character_
from pydantic import parse_obj_as


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
    # breakpoint()
    # characters = parse_obj_as(list(characters), Character_)
    response = {
        "count": data.get("count"),
        "message": "successful"
    }
    breakpoint()
    # return Response(response, status=200, mimetype="application/json")
    return response




