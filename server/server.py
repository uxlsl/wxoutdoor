from flask import Flask, Response, request, jsonify

from utils import (HT, get_activity, get_activitys_by_page,
                   get_activity_outdoor_agg)

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


@app.route('/art_agg')
def arg_agg():
    before = int(request.args.get('before', 1))
    results = get_activity_outdoor_agg(before)
    return jsonify(list(results))


@app.route('/hello')
def hello():
    page = request.args.get('page', 1)
    pagesize = request.args.get('pagesize', 10)
    before = request.args.get('before', None)
    key = request.args.get('key', '')
    return jsonify(list(
        get_activitys_by_page(page, pagesize,
                              before, key)))


if __name__ == '__main__':
    app.run(debug=True)
