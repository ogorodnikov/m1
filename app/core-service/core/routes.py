from core import app, login_manager, models, egcd

from flask import render_template, redirect, url_for, flash, request, jsonify

import botocore.exceptions

from flask_login import login_user, logout_user, login_required, current_user
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    
    print("Loading user")
    
    quit()
    
    return "dummy_user_id"


@app.route("/")
@app.route("/home")
def home():
    
    # return jsonify({"message" : "M1 Core Service V.11"})

    return render_template("home.html")
    
    
@app.route("/login")
def login():
    
    domain_name = 'ogoro'
    region = 'us-east-1'
    
    # login_endpoint = f'https://{domain_name}.auth.{region}.amazoncognito.com/login?'
    login_endpoint = 'https://auth.ogoro.me/login?'
    
    client_id = '19a0cvebjtej10gesr5r94qfqv'
    redirect_uri = 'https://9bca7b3479d64496983d362806a38873.vfs.cloud9.us-east-1.amazonaws.com/home'
    
    response_type = 'code'
    scope = 'email+openid'
    state = 'login_ok'
    
    login_url = login_endpoint + \
                f'client_id={client_id}&' + \
                f'redirect_uri={redirect_uri}&' + \
                f'response_type={response_type}&' + \
                f'scope={scope}&' + \
                f'state={state}'
                
    print("Login URL:", login_url)
    
    return redirect(login_url)
    

# @app.route("/logged-in")
# def logged_in():
    
#     print("Request args:", request.args)
    
#     return redirect(url_for('home'))
    
    
    
###
    

@app.route('/algorithms')
# @login_required
def get_algorithms():
    
    if not request.args:
        
        items = models.get_all_algorithms()
    
    else:
        
        try:
            items = models.query_algorithms(request.args)
            
        except botocore.exceptions.ClientError:
            items = models.get_all_algorithms()
        
    return render_template("algorithms.html", items=items)
    
    
@app.route('/algorithms/<algorithm_id>')
def get_algorithm(algorithm_id):
    
    item = models.get_algorithm(algorithm_id)
    
    return render_template("algorithm.html", item=item)
    
    
@app.route("/algorithms/<algorithm_id>/like")
# @login_required
def like_algorithm(algorithm_id):
    
    response = models.like_algorithm(algorithm_id)
    
    return response, 204
    
    
@app.route("/algorithms/<algorithm_id>/run")
def run_algorithm(algorithm_id):
    
    print('Ok')
    
    run_values = request.args.values()
    
    run_int_values = map(int, run_values)
    
    result = egcd.egcd(*run_int_values)
    
    print(result)
    
    # for e in run_values.items():
    #     print(e)
    
    # if run_values is not None:
        
    #     service_response = runner.run_with_values(run_values)
        
    # else:

    #     service_response = runner.run_default()

    # flask_response = Response(service_response)
    # flask_response.headers["Content-Type"] = "application/json"

    return jsonify({"output": result})




    

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
