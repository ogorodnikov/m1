from core import app, login_manager, models

from flask import render_template, redirect, url_for, flash, request, jsonify

from flask_login import login_user, logout_user, login_required, current_user
from flask_login import UserMixin

import botocore.exceptions
import json


@login_manager.user_loader
def load_user(user_id):
    return "dummy_user_id"


@app.route("/")
@app.route("/home")
def test():
    
    # return jsonify({"message" : "M1 Core Service V.11"})

    return render_template("home.html")
    
    
@app.route('/algorithms')
# @login_required
def get_algorithms():
    
    if not request.args:
        
        items = json.loads(models.get_all_algorithms())
    
    else:
        
        try:
            items = json.loads(models.query_algorithms(request.args))
        except botocore.exceptions.ClientError:
            items = json.loads(models.get_all_algorithms())
        
    return render_template("algorithms.html", items=items)
    
    
@app.route('/algorithms/<algorithm_id>')
def get_algorithm(algorithm_id):
    
    item = json.loads(models.get_algorithm(algorithm_id))
    
    return render_template("algorithm.html", item=item)
    
    
# @app.route("/m1/<algorithm_id>/like", methods=['POST'])
# def like_algorithm(algorithm_id):
    
#     service_response = table_client.like_algorithm(algorithm_id)

#     flask_response = Response(service_response)
#     flask_response.headers["Content-Type"] = "application/json"

#     return flask_response
    

# @app.route("/login")
# def login():
#     domain_name = 'm1.ogoro.me'
#     region = 'us-east-1'

#     loginendpoint = 'https://' + domain_name + '.auth.' + region + '.amazoncognito.com/oauth2/authorize?'
#     response_type = 'code'
#     scope = 'openid profile'
    
#     loginurl = loginendpoint + 'response_type=' + response_type + '&client_id=' + clint_id + '&scope=' + scope + '&redirect_uri=' + redirect_uri

#     return redirect(loginurl)

    

# @app.route("/m1", methods=['GET'])
# def get_algorithms():

#     filter_category = request.args.get('filter')
    
#     if filter_category is not None:
        
#         filter_value = request.args.get('value')
        
#         query_parameters = {'filter': filter_category,
#                             'value': filter_value}
                      
#         service_response = table_client.query_algorithms(query_parameters)
        
#     else:

#         service_response = table_client.get_all_algorithms()

#     flask_response = Response(service_response)
#     flask_response.headers["Content-Type"] = "application/json"

#     return flask_response
    
    

    


    

# @app.route("/m1/<algorithm_id>/state", methods=['POST'])
# def set_algorithm_state(algorithm_id):
    
#     state = request.args.get('state')
    
#     service_response = table_client.set_algorithm_state(state)
        
#     flask_response = Response(service_response)
#     flask_response.headers["Content-Type"] = "application/json"

#     return flask_response
    

# @app.route("/m1/<algorithm_id>/run", methods=['POST'])
# def run_algorithm(algorithm_id):
    
#     run_values = request.args.get('values')
    
#     if run_values is not None:
        
#         service_response = runner.run_with_values(run_values)
        
#     else:

#         service_response = runner.run_default()

#     flask_response = Response(service_response)
#     flask_response.headers["Content-Type"] = "application/json"

#     return flask_response