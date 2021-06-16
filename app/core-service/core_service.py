from flask import Flask, jsonify, json, Response, request, render_template
from flask_cors import CORS
import table_client
import runner
# import os

app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

CORS(app)


@app.route("/")
def health_check_response():
    
    return jsonify({"message" : "M1 Core Service V.9"})


@app.route("/test")
def test_response():

    # response = Response(open("test-response.json", "rb").read())
    # response.headers["Content-Type"]= "application/json"

    # return response
    
    return render_template("index.html")
    

@app.route("/m1", methods=['GET'])
def get_algorithms():

    filter_category = request.args.get('filter')
    
    if filter_category is not None:
        
        filter_value = request.args.get('value')
        
        query_parameters = {'filter': filter_category,
                            'value': filter_value}
                      
        service_response = table_client.query_algorithms(query_parameters)
        
    else:

        service_response = table_client.get_all_algorithms()

    flask_response = Response(service_response)
    flask_response.headers["Content-Type"] = "application/json"

    return flask_response
    
    
@app.route("/m1/<algorithm_id>", methods=['GET'])
def get_algorithm(algorithm_id):
    
    service_response = table_client.get_algorithm(algorithm_id)

    flask_response = Response(service_response)
    flask_response.headers["Content-Type"] = "application/json"

    return flask_response
    

@app.route("/m1/<algorithm_id>/like", methods=['POST'])
def like_algorithm(algorithm_id):
    
    service_response = table_client.like_algorithm(algorithm_id)

    flask_response = Response(service_response)
    flask_response.headers["Content-Type"] = "application/json"

    return flask_response
    

@app.route("/m1/<algorithm_id>/state", methods=['POST'])
def run_algorithm(algorithm_id):
    
    state = request.args.get('state')
    
    service_response = table_client.set_algorithm_state(state)
        
    flask_response = Response(service_response)
    flask_response.headers["Content-Type"] = "application/json"

    return flask_response
    

@app.route("/m1/<algorithm_id>/run", methods=['POST'])
def run_algorithm(algorithm_id):
    
    run_values = request.args.get('values')
    
    if run_values is not None:
        
        service_response = runner.run_with_values(run_values)
        
    else:

        service_response = runner.run_default()

    flask_response = Response(service_response)
    flask_response.headers["Content-Type"] = "application/json"

    return flask_response
    

if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=8080)
