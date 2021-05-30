from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS


app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

CORS(app)


@app.route("/")
def health_check_response():
    
    return jsonify({"message" : "Test ok) Try /m1"})


@app.route("/m1")
def test_response():

    response = Response(open("test-response.json", "rb").read())

    response.headers["Content-Type"]= "application/json"

    return response


if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=8080)
