#!/usr/bin/python3

import os

from flask import Flask, request, make_response, jsonify, Response
from flask_cors import CORS
from amazonia import amz
import yaml

app = Flask(__name__)
CORS(app)


@app.route('/yaml', methods=['POST', 'OPTIONS'])
def get_cloud_formation():

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    text_content = request.get_data(as_text=True)
    json_content = yaml.safe_load(text_content)
    default_yaml = amz.read_yaml(os.path.join(__location__, '../amazonia/defaults.yaml'))

    result = amz.generate_template(json_content, default_yaml)

    return Response(result, mimetype='Application/json')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(Exception)
def all_exception_handler(error):
    return make_response(jsonify({'error': str(error)}), 422)


@app.errorhandler(405)
def no_permission(error):
    return make_response(jsonify({'error': 'You do not have the required permissions to access this URL'}), 405)


@app.errorhandler(500)
def no_permission(error):
    return make_response(jsonify({'error': str(error)}), 500)

if __name__ == '__main__':
    app.run('0.0.0.0')
