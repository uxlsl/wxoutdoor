from flask import Flask
from flask_restful import Resource, Api,reqparse

from utils import get_activity_by_page



app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('pagesize', type=int)
        args = parser.parse_args()
        return list(get_activity_by_page(args['page'],
            args['pagesize']))

api.add_resource(HelloWorld, '/hello')


if __name__ == '__main__':
    app.run(debug=True)
