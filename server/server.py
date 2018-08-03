from flask import Flask,request,Response
from flask_restful import Resource, Api,reqparse

from utils import HT, get_activity, get_activitys_by_page



app = Flask(__name__)
api = Api(app)


@app.route('/art')
def art():
    type = request.args.get('type', 'html')
    content = get_activity(request.args.get('fileid'))['content']
    if type == 'markdown':
        content = HT.handle(content)
        return Response(content, mimetype='text/markdown')
    return content


class HelloWorld(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('pagesize', type=int)
        parser.add_argument('before', type=int)
        parser.add_argument('key', type=str)
        args = parser.parse_args()
        return list(get_activitys_by_page(args['page'],
            args['pagesize'],
            args['before'],
            args['key']))

api.add_resource(HelloWorld, '/hello')


if __name__ == '__main__':
    app.run(debug=True)
