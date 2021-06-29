from core import app, login_manager, models, egcd

from flask import render_template, redirect, url_for, flash, request, jsonify

from flask_login import login_user, logout_user, login_required, current_user
from flask_login import UserMixin

from flask_awscognito import AWSCognitoAuthentication

import botocore.exceptions
import requests
import base64

import boto3


@login_manager.user_loader
def load_user(user_id):
    
    print("Loading user")
    
    quit()
    
    return "dummy_user_id"



USER_POOL = 'm1-user-pool'


client = boto3.client('cognito-idp')

def get_user_pool_id(USER_POOL):

    user_pool_response = client.list_user_pools(MaxResults=60)
    
    user_pools = user_pool_response['UserPools']
    
    user_pool_id = next(attribute['Id'] for attribute in user_pools
                        if attribute['Name'] == USER_POOL)
                        
    return user_pool_id
    

app.config['AWS_DEFAULT_REGION'] = 'us-east-1'
app.config['AWS_COGNITO_DOMAIN'] = 'auth.ogoro.me'
app.config['AWS_COGNITO_USER_POOL_ID'] = get_user_pool_id(USER_POOL)
app.config['AWS_COGNITO_USER_POOL_CLIENT_ID'] = '19a0cvebjtej10gesr5r94qfqv'
app.config['AWS_COGNITO_USER_POOL_CLIENT_SECRET'] = ''
app.config['AWS_COGNITO_REDIRECT_URL'] = 'https://9bca7b3479d64496983d362806a38873.vfs.cloud9.us-east-1.amazonaws.com/logged-in'



aws_auth = AWSCognitoAuthentication(app)


@app.route('/login')
def login():
    
    return redirect(aws_auth.get_sign_in_url())
    

@app.route("/logged-in")
def logged_in():
    
    access_token = aws_auth.get_access_token(request.args)
     
    response = client.get_user(AccessToken=access_token)

    user_attributes = response['UserAttributes']
    user_sub = next(attribute['Value'] for attribute in user_attributes
                    if attribute['Name'] == 'sub')
    
    print('Access token:', access_token)
    print()
    print('Response:', response)
    print()
    print('User sub:', user_sub)


    return redirect(url_for('home'))
    

###


@app.route("/")
@app.route("/home")
def home():
    
    # return jsonify({"message" : "M1 Core Service V.11"})
    
    return render_template("home.html")
    

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
