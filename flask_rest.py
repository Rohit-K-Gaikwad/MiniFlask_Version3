"""
commands:


`pip install Flask-RESTful`
"""

from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

# runtime database (in-memory database)
my_resource1 = []
my_resource2 = []


class Resource1(Resource):
    def get(self):
        return my_resource1

    def post(self):
        request_data = request.json
        my_resource1.append(request_data)
        return request_data


class Resource2(Resource):
    def get(self):
        return my_resource2

    def post(self):
        request_data = request.json
        my_resource2.append(request_data)
        return request_data


# URL-biding
api.add_resource(Resource1, '/resource1')
api.add_resource(Resource2, '/resource2')

if __name__ == '__main__':
    app.run(debug=True)
