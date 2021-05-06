from flask import Flask, render_template, request, send_from_directory
from graphql_server.flask import GraphQLView
from flask_cors import CORS
from gql.schema import Schema
from dotenv import load_dotenv

import os
import signal
import subprocess
import time
import threading
import sys

import ssl

load_dotenv('.env')

ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__, static_url_path='', template_folder='./public', static_folder='./public')
CORS(app)

@app.route('/')
def home():
    return 'This is a flask microserver server !'
    #return app.send_static_file('index.html')
    #return send_from_directory('home', './public/home')

@app.errorhandler(404)
@app.route("/404")
def page_not_found(error):
    return app.send_static_file('404.html')

@app.errorhandler(500)
@app.route("/500")
def requests_error(error):
    return app.send_static_file('500.html')

#point GraphQL playground to /graphql endpoint
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
    'graphql',
    schema=Schema.graphql_schema,
    graphiql=True,
    pretty=True,
    #pass request to context to perform resolver validation
    get_context=lambda: {'request': request}
))

if __name__ == "__main__":
    print('TEST')
    app.run(host='0.0.0.0', ssl_context=('./secrets/cert.pem', './secrets/key.pem'))