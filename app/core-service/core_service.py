from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS
import algorithms_table_client

app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

CORS(app)


@app.route("/")
def health_check_response():
    
    return jsonify({"message" : "Test V.4 ok) Try /m1"})


@app.route("/m1")
def test_response():

    response = Response(open("test-response.json", "rb").read())

    response.headers["Content-Type"]= "application/json"

    return response
    
@app.route("/algorithms")
def get_algorithms():

    filter_category = request.args.get('filter')
    
    if filter_category is not None:
        
        filter_value = request.args.get('value')
        
        query_parameters = {'filter': filter_category,
                            'value': filter_value}
                      
        service_response = algorithms_table_client.query_algorithms(query_parameters)
        
    else:

        service_response = algorithms_table_client.get_all_algorithms()

    flask_response = Response(service_response)
    
    flask_response.headers["Content-Type"] = "application/json"

    return flask_response


if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=8080)
