from core import app, models, egcd, user

from flask import render_template, redirect, url_for, flash, request, jsonify

from flask_login import login_user, logout_user, login_required, current_user

from flask_awscognito import AWSCognitoAuthentication

import botocore.exceptions
import requests
import base64

import boto3



DEFAULT_REGION = 'us-east-1'
COGNITO_DOMAIN = 'auth.ogoro.me'
COGNITO_REDIRECT_URL = 'https://9bca7b3479d64496983d362806a38873.vfs.cloud9.us-east-1.amazonaws.com/logged-in'

USER_POOL = 'm1-user-pool'
USER_POOL_CLIENT = 'm1-user-pool-client'
USER_POOL_CLIENT_SECRET = ''



client = boto3.client('cognito-idp')


def get_user_pool_id(user_pool):

    user_pool_response = client.list_user_pools(MaxResults=60)
    
    user_pools = user_pool_response['UserPools']
    
    user_pool_id = next(attribute['Id'] for attribute in user_pools
                        if attribute['Name'] == user_pool)
                        
    return user_pool_id
    

def get_user_pool_clients(user_pool_id):

    user_pool_clients_response = client.list_user_pool_clients(UserPoolId=user_pool_id,
                                                               MaxResults=60)
                                                        
    # print("UPC", user_pool_clients_response)
    
    user_pool_clients = user_pool_clients_response['UserPoolClients']
    
    # print(user_pool_clients)
    
    user_pool_client_id = next(attribute['ClientId'] for attribute in user_pool_clients
                               if attribute['ClientName'] == USER_POOL_CLIENT)
                        
    return user_pool_client_id


user_pool_id = get_user_pool_id(USER_POOL)
user_pool_client_id = get_user_pool_clients(user_pool_id)

# print('UPCI', user_pool_client_id)


app.config['AWS_DEFAULT_REGION'] = DEFAULT_REGION
app.config['AWS_COGNITO_DOMAIN'] = COGNITO_DOMAIN
app.config['AWS_COGNITO_USER_POOL_ID'] = user_pool_id
app.config['AWS_COGNITO_USER_POOL_CLIENT_ID'] = user_pool_client_id
app.config['AWS_COGNITO_USER_POOL_CLIENT_SECRET'] = USER_POOL_CLIENT_SECRET
app.config['AWS_COGNITO_REDIRECT_URL'] = COGNITO_REDIRECT_URL

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
    
    
    new_user = user.User(user_sub)
    print("New user:", new_user.id)
    
    print("Before - User loaded:", current_user)
    
    login_user(new_user)
    
    print("After - User loaded:", current_user)

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
