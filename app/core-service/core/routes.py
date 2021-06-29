from core import app, login_manager, models, egcd

from flask import render_template, redirect, url_for, flash, request, jsonify

from flask_login import login_user, logout_user, login_required, current_user
from flask_login import UserMixin

import botocore.exceptions
import requests
import base64


@login_manager.user_loader
def load_user(user_id):
    
    print("Loading user")
    
    quit()
    
    return "dummy_user_id"
    



domain_name = 'ogoro'
region = 'us-east-1'

# login_endpoint = f'https://{domain_name}.auth.{region}.amazoncognito.com/login?'

login_endpoint = 'https://auth.ogoro.me/login?'
token_endpoint = 'https://auth.ogoro.me/oauth2/token'


### m1-user-pool

# client_id = '19a0cvebjtej10gesr5r94qfqv'
# client_secret = ''


### m1-user-pool2

client_id = 'o7onq15ivu5terh6sajs4mq9'
client_secret = '1drvkg92suec576ebsdcq0sjv1vqfb17ph5krfnu0v81l94rbp0k'
### bzdvbnExNWl2dTV0ZXJoNnNhanM0bXE5OjFkcnZrZzkyc3VlYzU3NmVic2RjcTBzanYxdnFmYjE3cGg1a3JmbnUwdjgxbDk0cmJwMGs=

url_root = 'https://9bca7b3479d64496983d362806a38873.vfs.cloud9.us-east-1.amazonaws.com'
redirect_logged_in = url_root + '/logged-in'
redirect_home = url_root + '/home'

response_type = 'code'
scope = 'email+openid'
state = 'state_ok'


@app.route("/login")
def login():
    
    login_url = login_endpoint + \
                f'client_id={client_id}&' + \
                f'redirect_uri={redirect_logged_in}&' + \
                f'response_type={response_type}&' + \
                f'scope={scope}&' + \
                f'state={state}'
                
    print('>>>> Login URL:', login_url)

    return redirect(login_url)
    

@app.route("/logged-in")
def logged_in():
    
    code, state = map(request.args.get, ('code', 'state'))
    
    auth_base = base64.b64encode(f'{client_id}:{client_secret}'.encode())
    
    authorization = 'Basic ' + auth_base.decode()
    
    print('  Token endpoint:', token_endpoint)
    print('  Authorization:', authorization)
    print('  Code:', code)
    print('  Client ID:', client_id) 
    print('  Redirect Home:', redirect_home)
    

    response = requests.post(token_endpoint,
    
                {'Content-Type':'application/x-www-form-urlencoded',
                 'Authorization': authorization,
                #  'client_secret': client_secret,
                 'grant_type': 'authorization_code',
                 'client_id': client_id,
                 'code': code,
                 'redirect_uri': redirect_home})
                 
    print('Logged-in response:', response.json())
    
    
    # POST https://auth.ogoro.me.us-east-1.amazoncognito.com/oauth2/token&
    #                   Content-Type='application/x-www-form-urlencoded'&
    #                   Authorization=Basic aSdxd892iujendek328uedj
                       
    #                   grant_type=authorization_code&
    #                   client_id=djc98u3jiedmi283eu928&
    #                   code=AUTHORIZATION_CODE&
    #                   redirect_uri=com.myclientapp://myclient/redirect
                       

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
